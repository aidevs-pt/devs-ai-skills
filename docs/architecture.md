# Repository architecture

## One source of truth

`.agents/skills/<slug>/` contains the original installable package. This shared native
location is documented by Codex, Cursor, Gemini CLI, and VS Code. Claude uses the
declared plugin path or a copy installed into its native directory.

`SKILL.md` supplies runtime name, description, and workflow. `skill.json` adds release,
category, buyer, search, and service metadata without polluting portable frontmatter.
`config/repository.json` holds identity and publication configuration. `bundles.json`
contains curated collection membership.

## Repository areas

| Area | Purpose |
|---|---|
| `.agents/skills/` | Canonical standalone workflow packages |
| `.claude-plugin/` | Generated Claude manifest and local marketplace |
| `.codex-plugin/` | Generated Codex compatibility manifest |
| `.github/agents/` | VS Code Copilot authoring agent |
| `.github/instructions/`, `.cursor/rules/` | Scoped authoring guidance |
| `scripts/` | Original catalog, installer, scaffolder, validator, and packager |
| `cli/` | Optional Node wrapper and generated machine catalog |
| `standards/`, `templates/` | Authoring contract, context/evaluation templates, shared helper source |
| `tests/` | Independent business assertions and repository tooling tests |
| `docs/` | Human guidance, research, and actual verification report |
| `website/content/` | Generated, unpublished content for aidevs.pt pages |
| `downloads/` | Generated individual and collection ZIPs, with checksums |

## Deterministic generation

`scripts/build_manifest.py` derives registry.json, skills.json, cli/skills.json,
Codex/Gemini browsing indexes, plugin manifests, domain indexes, and website content.
It adds no wall-clock timestamps. `--check` detects drift without writing.

`scripts/package.py` creates real-file archives with fixed ZIP metadata and checksums.
There are no symlinks to fail after a Windows extraction. A skill never imports a
repository script or another skill. Its helper module is bundled locally.

## Deliberate changes from the reference

We preserve its package/catalog/installer/standards pattern while consolidating the
native skill tree. We do not copy older Codex symlink views or Gemini Markdown wrappers.
We avoid duplicate native skill copies and inconsistent hand-maintained counts.

The ten workflows need no MCP execution server or credentials. Live connectors,
provider calls, hosted operation, automatic repository writes, and npm publishing
are outside the initial package. They can be added when there is a concrete need.
