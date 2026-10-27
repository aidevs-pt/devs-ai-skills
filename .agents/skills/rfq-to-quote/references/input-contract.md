# Input contract

currency string; catalog with unique sku, approved boolean, unit_price, currency, price_source; request array with unique id/sku/quantity. Optional tax_rate is a fraction from 0 to 1 and requires tax_rule_source.

The helper rounds each line and then tax to two decimal places with half-up rounding.
Use it only when that supplied commercial rounding rule and the currency precision
are appropriate. Other currency precisions or jurisdiction-specific invoice rules
require a reviewed calculation change; the helper does not infer them.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

request line | sku | quantity | unit price | line total | price source | exception | draft status

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
