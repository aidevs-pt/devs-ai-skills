"""Small, self-contained file helpers bundled with each DEVS AI skill."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    def bad(value):
        raise ValueError(f"Non-finite JSON number: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=pairs, parse_constant=bad)


def number(value, field="number", minimum=None):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be a finite number")
    try:
        n = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not n.is_finite() or (minimum is not None and n < Decimal(str(minimum))):
        raise ValueError(f"Invalid {field}: {value}")
    return n


def rows(value, field):
    if not isinstance(value, list) or any(not isinstance(x, dict) for x in value):
        raise ValueError(f"{field} must be an array of objects")
    return value


def index(items, field="id"):
    result = {}
    for row in rows(items, "records"):
        raw = row.get(field)
        if not isinstance(raw, str) or not raw.strip() or raw != raw.strip():
            raise ValueError(f"{field} must be a non-empty trimmed string")
        key = raw
        if key in result:
            raise ValueError(f"Missing or duplicate {field}: {key}")
        result[key] = row
    return result


def csv_cell(value):
    """Avoid active spreadsheet formulas when exporting untrusted strings."""
    text = str(value)
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text


def save(path, text, overwrite=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise ValueError(f"Output exists; use --overwrite to replace it: {path}")
    fd, temp = tempfile.mkstemp(prefix=".devs-ai-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            out.write(text)
        if not overwrite:
            # Hard-link makes the no-overwrite condition atomic.
            os.link(temp, path)
            os.unlink(temp)
        else:
            os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run(process, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input", type=Path, required=True, help="Supplied JSON input; see assets/example-input.json")
    parser.add_argument("--output", type=Path, help="Write JSON to this file; default: stdout")
    parser.add_argument("--overwrite", action="store_true", help="Replace the explicitly selected output file")
    args = parser.parse_args()
    try:
        data = read_json(args.input)
        if not isinstance(data, dict):
            raise ValueError("Input root must be an object")
        result = process(data)
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            save(args.output, text, args.overwrite)
        else:
            sys.stdout.write(text)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Input/output error: {exc}\n")
