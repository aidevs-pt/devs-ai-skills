# Installation and first run

Extract the repository ZIP to a normal writable directory. Open that root in your
editor. For terminal commands, use Python 3.10+ (`python`, `python3`, or `py` according
to your installation). No pip install is required.

## In this repository

Codex, Cursor, Gemini CLI, and VS Code can discover the canonical `.agents/skills/`
workspace directory according to their current documentation. Discovery does not
guarantee a skill will activate automatically: explicitly request the named skill
and inspect the loaded file path. Enterprise policies and client versions can differ.

For Claude Code, load the repository as a local plugin marketplace:

```text
/plugin marketplace add .
/plugin install devs-ai-business-skills@devs-ai-marketplace
```

Alternatively use `claude --plugin-dir /absolute/path/to/devs-ai-skills` if supported
by your installed client, or use the copy-based installer below. Do not install the
same collection through multiple methods in the same client.

## In another project

```bash
python scripts/devs.py install supplier-catalog-to-store --agent copilot --scope project --project /path/to/project --dry-run
python scripts/devs.py install supplier-catalog-to-store --agent copilot --scope project --project /path/to/project
```

Choose a collection with `--bundle starter`, `commerce`, or `operations`, or use `--all`.
Choose `--scope user` only when you intentionally want a user-level installation.
Use [the compatibility table](compatibility.md) to see the exact destination.

The local installer performs no download or provider call. It uses the source files
in this checkout. It preflights destination conflicts, records content hashes, and
refuses to replace unmanaged or locally changed packages.

```bash
python scripts/devs.py status --agent copilot --project /path/to/project
python scripts/devs.py update --agent copilot --project /path/to/project --dry-run
python scripts/devs.py remove supplier-catalog-to-store --agent copilot --project /path/to/project --dry-run
```

Update after you update this source checkout. Removal requires a matching ownership
record and unchanged contents. Modified packages must be preserved/resolved manually.
Multi-skill operations preflight all conflicts; each skill replacement is individually
atomic, not a cross-skill database transaction. Do not run concurrent installer processes.

## Try an example

Ask your assistant: "Use supplier-catalog-to-store with its synthetic example and
produce the catalog CSV plus an exception list." The full skill asks the host to
perform language work and review; the helper alone prepares deterministic evidence.

Run that helper directly from its installed folder:

```bash
python scripts/prepare_catalog.py --input assets/example-input.json
```

For the finder, write a real local prototype from its installed folder:

```bash
python scripts/build_finder.py --input assets/example-input.json --html-output finder.html
```

Source paths are relative to SKILL.md. Existing outputs are not replaced unless
`--overwrite` is supplied. Keep your own source data outside the public repository.
