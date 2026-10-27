"""Shared repository tooling. Installed skills never depend on this module."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CATEGORIES = {"commerce", "support", "knowledge", "operations", "sales", "product", "strategy"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def identity(root=ROOT):
    return read_json(Path(root) / "config/repository.json")


def frontmatter(path):
    """Parse our deliberately small YAML subset; never execute arbitrary YAML tags."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"Missing frontmatter: {path}")
    end = lines[1:].index("---") + 1
    data = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep or key in data:
            raise ValueError(f"Invalid or duplicate frontmatter field: {path}")
        value = value.strip()
        data[key] = json.loads(value) if value.startswith('"') else value
    return data, "\n".join(lines[end + 1:])


def skill_dirs(root=ROOT):
    return sorted((Path(root) / ".agents/skills").glob("*/SKILL.md"))


def catalog(root=ROOT):
    result = []
    for path in skill_dirs(root):
        meta = read_json(path.parent / "skill.json")
        fm, _ = frontmatter(path)
        result.append({**meta, "name": fm["name"], "description": fm["description"],
                       "path": path.parent.relative_to(root).as_posix()})
    return sorted(result, key=lambda s: (s["priority"], s["name"]))


def safe_package(root, name):
    if not isinstance(name, str) or not SLUG.fullmatch(name) or len(name) > 64:
        raise ValueError("Invalid skill name")
    path = Path(root) / ".agents/skills" / name
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"Unknown or symlinked skill: {name}")
    if path.resolve().parent != (Path(root) / ".agents/skills").resolve():
        raise ValueError("Skill escaped its root")
    return path


def tree_hash(path):
    digest = hashlib.sha256()
    for f in sorted(Path(path).rglob("*")):
        if f.is_symlink():
            raise ValueError(f"Symlinks are not allowed in packages: {f}")
        if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc":
            digest.update(f.relative_to(path).as_posix().encode())
            digest.update(b"\0")
            digest.update(f.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()
