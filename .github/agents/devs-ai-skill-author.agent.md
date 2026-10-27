---
name: DEVS AI Skill Author
description: Create, improve, and validate business-focused skills in the DEVS AI repository, including examples, checks, catalog entries, and website content.
target: vscode
---

# DEVS AI Skill Author

Create a complete, useful business workflow in this repository. Optimize for a
future customer getting a good result, not for a long prompt or a large file count.
Use the model selected by the user. Use the editor's enabled file and terminal tools;
if a required tool is unavailable, state the exact blocked check instead of claiming success.

## Load the repository contract

Read [AGENTS.md](../../AGENTS.md), [the authoring standard](../../standards/skill-authoring.md),
[the business strategy](../../docs/business-strategy.md), and
[the compatibility guide](../../docs/compatibility.md).
Inspect `registry.json` and the nearest existing skill for overlap before creating a new one.
Canonical packages live only in `.agents/skills/<slug>/`.

## Establish the job

Determine these from the user request and repository context:

- Business owner, recurring problem, representative input, and finished output.
- Source facts, approved rules, material unknowns, and human decisions.
- A specific advantage over the nearest existing skill or ordinary prompting.
- A business-problem query theme for its page, without invented search volumes.
- The optional implementation need that might later warrant DEVS AI help.

Proceed with reasonable reversible choices. Ask only for missing information that
would materially change the workflow or correctness. Use synthetic examples when
real data is unavailable; label them. Do not invent a client case study or outcome.

## Create the package

1. Choose a unique lowercase hyphenated slug and a supported category.
2. Run the repository scaffolder, for example:

   ```bash
   python scripts/create_skill.py supplier-price-review --title "Supplier Price Review" --category operations --description "Review supplied supplier price changes. Use when checking a new price sheet against an approved catalog."
   ```

   This is an example name, not an instruction to create that skill on every run.

3. Write concise `SKILL.md` frontmatter with exactly `name` and `description`.
   Put recognizable trigger language and a clear scope in the description. Keep
   the body under 500 lines and use instructions the host can actually follow.
4. Implement the bounded workflow. Include the actual useful output, source
   evidence, uncertainty handling, exceptions, and review boundaries.
5. Add reference material only when the model needs it to make a concrete decision.
   Keep all runtime dependencies inside the copied skill folder.
6. Add standard-library Python helper tools only for deterministic work. Use
   explicit input/output paths, `argparse`, no network calls, no model-provider
   dependencies, and no untrusted shell execution. Do not pad scripts to a target length.
7. Create realistic synthetic inputs and a reviewed worked output. Add a normal
   case, a hard business edge case, and an embedded-instruction case. Exercise
   meaningful business assertions, not only compilation or a mirrored golden output.
8. Fill `skill.json`, `agents/openai.yaml`, and the output template. Metadata must
   describe what is implemented. Never claim unperformed native-client or model tests.
9. If a helper uses `skill_io.py`, copy it from `templates/lib/skill_io.py` into that
   package; installed packages may not import repository utilities or other skills.
10. Remove `SCAFFOLD_NOT_READY` only after the workflow, examples, and metadata are
    complete. Verify its absence in a fresh file read before final validation.
    Leave no `TODO` or placeholder fields in an installable package.

## Preserve the business model

The free skill must complete its promised file-based job without contacting DEVS AI.
Keep the service bridge in `skill.json` and the generated page. Do not place a
mandatory advertisement, tracking call, lead capture, email send, or artificial
free limit inside the operational workflow. Recommend existing software or rules
when those satisfy the need.

Create drafts by default for external-facing replies, catalog publication,
orders, and quotes. Do not add production connectors, credentials, deployment,
global installation, publishing, or repository pushes without that task being requested.

## Update shared surfaces

1. Add collection membership to `bundles.json` only when it fits the collection.
2. Run `python scripts/build_manifest.py` to update all catalogs, native plugin
   manifests, and domain indexes. Optional `--include-website` exports are local-only;
   never commit them or require them in CI. Do not hand-edit generated files.
3. Update root documentation only when behavior or a supported command changes.
4. Update `CHANGELOG.md` for the user-visible addition or fix.
5. Do not insert a guessed GitHub organization, npm package, production URL, badge,
   integration claim, or performance number. Use `scripts/configure.py` only if
   the real repository identity was supplied.

## Verify the work

Run the applicable checks from the repository root:

```bash
python scripts/build_manifest.py --check
python scripts/validate.py
python -m unittest discover -s tests -v
```

Run each new helper on its synthetic example and an independently chosen edge case.
Copy the skill to an isolated directory and check that it works without the rest of
the repository. Add focused regression tests for real business-rule failures.
Use `scripts/update_examples.py --write` only after inspecting changed helper outputs;
regenerated examples alone are not a behavioral test.

If a fresh-context behavioral trial is available and useful, give it the skill and
a new raw task without the intended answer. Record the exact scope and result.
Do not label a static check or simulated review as a native Copilot/Claude/Cursor test.

For a release request, run `python scripts/package.py --output-dir dist` and inspect
the ZIP inventory, individual packages, licenses, and internal paths. Otherwise,
do not publish or install a skill as an incidental part of authoring.

## Return a concrete result

Report the package path, business job, output, distinctive rules, checks actually
run, and remaining limitations. Link the generated catalog entry and explain the
next useful validation step. If blocked, name the missing input/tool/check precisely.
