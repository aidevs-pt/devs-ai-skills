# DEVS AI Business Skills

Free, reusable AI workflows for useful business work: prepare a catalog, draft
order-support replies, answer company-document questions, and process operational data.
Built for the open Agent Skills format and the people who own these business jobs.

[DEVS AI](https://www.aidevs.pt) | [AI services](https://www.aidevs.pt/ai-services) |
[Skill catalog](docs/skills-reference.md) | [Installation](docs/installation.md) |
[Create a skill](docs/authoring.md)

## Start with a business job

- **Supplier Catalog to Store:** supplier data to reviewed product records and copy.
- **E-commerce Support Copilot:** order-aware draft replies and actionable exceptions.
- **Company Knowledge Q&A:** company answers with sources, versions, and explicit unknowns.
- **Purchase Order Intake:** incoming customer POs to matched sales-order drafts.
- **Product Finder Builder:** an editable local quiz using real catalog constraints.
- **SOP to AI Workflow:** a repeatable procedure and one completed work example.
- **RFQ to Quote:** a traceable draft from supplied approved prices.
- **Multilingual Catalog Launch:** localized records with invariant and revision checks.
- **Customer Feedback to Fixes:** customer evidence linked to a practical fix backlog.
- **AI Automation Opportunity Finder:** transparent scenarios and a feasible pilot brief.

Browse the [generated catalog](docs/skills-reference.md) for exact package paths.

## Skills installation

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

## Use it locally

Python 3.10+ is needed for helper tools and repository commands. They use the standard
library; there is no pip dependency to install. Your AI host/model may have its own costs.

```bash
python scripts/devs.py list
python scripts/devs.py search "catalog"
python scripts/devs.py info supplier-catalog-to-store
```

Open this folder in Codex, Cursor, Gemini CLI, or VS Code Copilot and verify skill
discovery. `.agents/skills/` is the canonical workspace tree. Claude Code can load
the local plugin or use the copy-based installer:

```bash
python scripts/devs.py install --bundle starter --agent claude --scope project --project /path/to/your/project --dry-run
python scripts/devs.py install --bundle starter --agent claude --scope project --project /path/to/your/project
```

For other tools, choose `--agent codex`, `cursor`, `copilot`, `gemini`, or `universal`.
The installer copies complete packages, records ownership, and refuses to overwrite
unmanaged or locally edited content. [All paths and caveats](docs/compatibility.md).

Individual skill ZIPs are in `downloads/skills/`; collection ZIPs are in
`downloads/bundles/` in the packaged release. Browser-host upload support depends on
that host, plan, and enabled features; those ZIPs are not a universal one-click promise.
