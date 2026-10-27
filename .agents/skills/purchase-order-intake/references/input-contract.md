# Input contract

catalog: sku/unit/aliases/unit_conversions/source. orders: unique id, customer_id, lines with unique id/product_code/quantity/unit/source. Conversion factors express base units per requested unit.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

order_id | customer_id | source line | matched sku | quantity | unit | exception | draft status

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
