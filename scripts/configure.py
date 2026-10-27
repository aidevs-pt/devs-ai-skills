"""Set repository identity and regenerate its derived catalogs."""
from __future__ import annotations

import argparse
import re
import sys
from repo import ROOT, identity, json_text, write
from build_manifest import outputs

GITHUB_REPOSITORY = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?/[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?$")


def configure(github_repository):
    if not GITHUB_REPOSITORY.fullmatch(github_repository):
        raise ValueError("Use a GitHub OWNER/REPOSITORY identifier, not a URL")
    config_path = ROOT / "config/repository.json"
    config = identity()
    config["github_repository"] = github_repository
    write(config_path, json_text(config))
    for name, text in outputs().items():
        write(ROOT / name, text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github", required=True, help="GitHub OWNER/REPOSITORY identifier")
    args = parser.parse_args()
    try:
        configure(args.github)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")
    print(f"Configured repository identity: {args.github}")


if __name__ == "__main__":
    sys.exit(main())
