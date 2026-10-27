# Create a new skill

## With Copilot

Open the repository root in VS Code. In Chat, select the Copilot harness and choose
**DEVS AI Skill Author**. Give it the recurring business job, supplied inputs,
desired artifact, and a difficult example. The agent uses the selected model and
enabled editing/terminal tools. It does not require a hardcoded model or MCP server.

If the agent is missing, inspect `.github/agents/devs-ai-skill-author.agent.md`, use
Chat: Open Customizations, and check the selected harness, workspace trust, policy,
and customization diagnostics. A file that parses locally is not proof the UI loaded it.

The included `new-skill.prompt.md` is an optional reusable entry point. The equivalent
Claude author wrapper is `.claude/agents/devs-ai-skill-author.md`.

## With the CLI

```bash
python scripts/create_skill.py supplier-price-review --title "Supplier Price Review" --category operations --description "Compare supplied supplier price sheets. Use when reviewing changed prices, units, or product codes."
```

This creates an intentionally incomplete scaffold. Fill the business instructions,
metadata, realistic examples, original rules, and meaningful checks. Remove
`SCAFFOLD_NOT_READY` only when complete. Scaffolding is not a finished skill.

The scaffolder is repository-specific. It does not install personal skills into an
AI account or change your machine's global configuration.

## Author checklist

1. Check the current catalog for overlap.
2. Complete the business brief in `templates/skill-brief.md`.
3. Follow `standards/skill-authoring.md`.
4. Keep runtime dependencies inside the package.
5. Test normal, edge, and untrusted-input cases, with an actual useful output.
6. Update collection membership only where appropriate.
7. Regenerate catalogs and website pages, then validate and run relevant tests.
8. Update the changelog and report remaining uncertainty honestly.

Use `python scripts/update_examples.py --write` to deliberately regenerate helper
examples after reviewing a change. Do not confuse a new golden file with an
independent correctness test. Instruction-only skills retain manually reviewed examples.

All new original contributions use the repository MIT notice. Do not copy another
publisher's content or tools without inspecting and honoring their actual terms.
