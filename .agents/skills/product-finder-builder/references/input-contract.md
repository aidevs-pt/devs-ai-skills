# Input contract

title string; products with unique id/name/price/currency/available boolean/attributes object and optional safe url; questions with unique id/label/options, each option containing label and where object.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

shopper journey | selected constraints | expected matches/no match | observed result | follow-up

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
