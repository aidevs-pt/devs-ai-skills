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
| `website/content/` | Optional, ignored local content exports; never distributed |
| `downloads/` | Generated individual and collection ZIPs, with checksums |

## Deterministic generation

`scripts/build_manifest.py` derives registry.json, skills.json, cli/skills.json,
Codex/Gemini browsing indexes, plugin manifests, and domain indexes.
It adds no wall-clock timestamps. `--check` detects drift without writing.
Generated catalogs and documentation are versioned so GitHub browsing, clones,
and source ZIP downloads include them without running Python.
Edit the source metadata, not the generated files.

The entire `website/` folder is local-only and ignored by Git. Website exports are
optional: use `python scripts/build_manifest.py --include-website` locally when
needed. Normal generation, drift checks, validation, and CI do not generate,
read, or require website content. Existing local files are left untouched, and
release archives exclude the folder even when it exists.

### Publishing generated text

[Publish generated catalogs and docs](../.github/workflows/publish-generated.yml)
runs after **Validate skills** succeeds for a push or manual validation on `master`
in this repository. It never publishes pull-request or fork results. The workflow
must already exist on the default branch for `workflow_run` to trigger it.

The publisher checks out the exact validated SHA, regenerates and validates the
outputs, and makes a follow-up bot commit on `master` only when content changed.
It stages only the approved catalog/index/manifest JSON files, `docs/skills-reference.md`,
and `docs/domains/*.md`. Obsolete generated pages are removed. Those paths are
generator-owned; do not put handwritten documents there. Website content, ZIPs,
logs, private data, and local evaluation records are not published by this workflow.

Runs are serialized. If `master` advances before publication, the outdated run is
skipped; the newer revision must pass validation before its outputs are published.
Pushes are fast-forward only, with no force-push or rebase. Original commits and
tags remain unchanged: their source downloads do not gain the follow-up files.
There is a short interval between a source change and the generated-file commit;
validation and packaging still regenerate locally rather than trusting snapshots.

Only the publishing job has `contents: write`. It uses the built-in `GITHUB_TOKEN`
(no personal token), so the bot's push does not recursively trigger validation.
Code on `master`, including the generator and publisher, must be trusted and reviewed;
passing tests alone is not a security boundary. Branch protection and organization
policies must permit this bot to push. Rejections fail visibly; the workflow does
not bypass protection. If mandatory PRs/signatures prevent direct writes, use a
reviewed generated-content PR process instead of granting a broad bypass.

See GitHub's [workflow_run security warning](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run)
and [GITHUB_TOKEN trigger behavior](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#triggering-a-workflow-from-a-workflow).

`scripts/package.py` creates real-file archives with fixed ZIP metadata and checksums.
There are no symlinks to fail after a Windows extraction. A skill never imports a
repository script or another skill. Its helper module is bundled locally.

## Deliberate changes from the reference

We preserve its package/catalog/installer/standards pattern while consolidating the
native skill tree. We do not copy older Codex symlink views or Gemini Markdown wrappers.
We avoid duplicate native skill copies and inconsistent hand-maintained counts.

The ten business workflows need no MCP execution server or credentials. Live connectors,
provider calls, hosted operation, and npm publishing are outside the initial package.
The generated-content CI publisher is a separate, repository-maintenance-only write
path; installed business skills still never publish or modify live systems by default.
