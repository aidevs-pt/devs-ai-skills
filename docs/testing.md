# Testing model

The repository separates five different kinds of evidence:

1. **Static validation:** names, files, links, portability, metadata, generated drift.
2. **Helper tests:** deterministic business assertions, invalid data, and output boundaries.
3. **Standalone/install tests:** a copied folder runs without the repository; installation
   refuses unmanaged or locally modified destinations and protects removal.
4. **Fresh-context task trials:** an agent uses a skill on new raw inputs, without the
   expected answer. These test workflow behavior in that environment only.
5. **Native client smoke tests:** an actual version of VS Code/Copilot, Claude Code,
   Cursor, Codex, or Gemini loads and executes the package.

The first three do not imply the last two. A helper output is not a complete model
benchmark, a security certification, or evidence of business ROI. All starter examples
are synthetic. Use real operator review before relying on the output in a business.

```bash
python scripts/build_manifest.py
python scripts/build_manifest.py --check
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/update_examples.py
node --test cli/test/cli.test.mjs tests/test_finder_runtime.mjs
```

Generated catalogs and documentation are tracked for readers and refreshed by the
[post-validation publisher](architecture.md#publishing-generated-text). The local-only
`website/` folder is excluded from test fixtures and is not required or checked by
normal validation or drift checks. CI still
regenerates it before checking; stale snapshots do not block the source change that
will refresh them. Publisher regression tests use isolated local Git repositories,
not GitHub credentials or live pushes. They do not prove that a repository's branch
rules allow the Actions bot to write.

Node.js is optional for users. That last command checks the optional CLI wrapper and
the product finder's generated JavaScript in a minimal DOM harness; it is not a
browser or native AI-client smoke test.

Evaluation cases inside skills are prompts and acceptance criteria, not records that
every model ran those cases. Use `templates/evaluation-result.json` to record an
actual experiment, including conditions, outcome, corrections, and remaining failures.

For model benefit, compare the same task with and without the skill under matched
conditions. Measure factual correctness, useful output, correction effort, and exceptions.
Do not publish a percentage improvement without the experiment and supporting data.
