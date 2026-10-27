# Compatibility and evidence

Research date: 27 October 2026. Supported packaging is based on the linked official
documentation. Native GUI/CLI activation must still be smoke-tested in the version
you use; it is separate from the automated local package and installer checks.

| Client | Project install destination | User install destination | Repository use |
|---|---|---|---|
| Claude Code | `.claude/skills/<slug>/` | `~/.claude/skills/<slug>/` | Local plugin declares `.agents/skills/` |
| Codex | `.agents/skills/<slug>/` | `~/.agents/skills/<slug>/` | Canonical tree; AGENTS.md guidance |
| Cursor | `.cursor/skills/<slug>/` | `~/.cursor/skills/<slug>/` | Also discovers canonical `.agents/skills/` |
| Copilot / VS Code | `.github/skills/<slug>/` | `~/.copilot/skills/<slug>/` | VS Code also discovers `.agents/skills/`; author is in `.github/agents/` |
| Gemini CLI | `.gemini/skills/<slug>/` | `~/.gemini/skills/<slug>/` | Also discovers `.agents/skills/` alias |
| Other skills-aware tools | `.agents/skills/<slug>/` when supported | `~/.agents/skills/<slug>/` when supported | Verify the host's own discovery rules |

The shared format does not make hooks, forked contexts, slash commands, tool names,
or permissions portable. These business skills use plain instructions and local
Python. The host supplies file access and language capabilities. No tool permissions
or approval bypasses are installed.

The Codex manifest contains local package metadata, not a completed marketplace
submission. Public listing may need additional publisher, privacy, and support details.
Individual ZIPs are ordinary skill folders, not a guarantee that every browser host
or account can upload/execute skills.

## Verify in a client

1. Use one installation method and open the intended workspace.
2. Check the host's skill list/diagnostics and confirm the loaded package path.
3. Explicitly invoke a skill with a synthetic example.
4. Confirm the host reads its reference files and runs the intended local helper.
5. Inspect the actual business output, unknowns, and review state.
6. Record client/version/model/date, prompt, outcome, and limitations using the template.

## Official sources

- [OpenAI skill creation and local discovery](https://learn.chatgpt.com/docs/build-skills)
- [Codex plugin metadata](https://developers.openai.com/plugins/deploy/submission)
- [Claude skills](https://code.claude.com/docs/en/skills)
- [Claude plugin manifests](https://code.claude.com/docs/en/plugins-reference)
- [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [VS Code custom-agent file reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference)
- [Cursor skills](https://cursor.com/docs/skills)
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)
- [Agent Skills standard](https://agentskills.io/specification)
