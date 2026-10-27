# Input contract

name; supplied_inputs array of strings; steps with unique id, type manual/rule/ai/review/external_action, inputs/outputs/depends_on arrays, and acceptance_check for AI steps.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

step | trigger/input | rule or AI task | output | acceptance check | review owner | exception path

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
