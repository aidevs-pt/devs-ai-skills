# Input contract

items array with unique id, non-empty text, optional customer_id/source_event_id/source/product/journey_stage/theme. The host supplies theme labels; unclassified records remain explicit.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

theme | product/journey | observed count | unique customers or unknown | evidence | proposed fix | validation

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
