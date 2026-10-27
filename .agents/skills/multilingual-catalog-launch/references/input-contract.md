# Input contract

target_locale; source records keyed by sku with variant_id/revision/facts/title/description; localized records keyed by sku with matching variant_id/source_revision/facts, locale, title, description.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

sku | locale | source revision | localized copy | invariant check | native review | update action

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
