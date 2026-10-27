# Input contract

tasks with unique id; runs_per_month/minutes_per_run/automatable_fraction/review_minutes_per_run required for a scenario. Optional hourly_cost/currency/evidence; fractions use 0..1.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

task | baseline evidence | scenario hours | review cost | omitted costs | alternatives | pilot decision

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
