# Input contract

products: array of records; sku/title/source strings; approved boolean; quantity optional decimal string with unit; attributes optional object. Alternatively supply supplier_csv as an approved path. CSV fields are case-sensitive.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

sku | title | variant | description | source | status

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
