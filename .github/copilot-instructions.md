# DEVS AI repository context

Follow [AGENTS.md](../AGENTS.md) and the [skill authoring standard](../standards/skill-authoring.md).
This is a collection of self-contained business workflows, not a hosted service.
Canonical skills live in `.agents/skills/`; `registry.json` is generated.

Use the **DEVS AI Skill Author** custom agent for creating or substantially changing
a package. Preserve the user's chosen model and enabled tools. Do not invent client
results, published repository identities, search volumes, or native-client test results.

After a package change, regenerate catalogs and run the validator plus relevant
unit/behavioral checks. Keep free business outputs useful and free of forced advertising.
