# Business rules

- Do not merge records solely because their titles match; variant identity comes first.

- A source pointer is evidence provenance, not proof the supplier claim is correct.

- Keep unpublished/unapproved records in the deliverable with a clear review state.

- For CSV input, supply supplier_csv as an explicitly approved file path; columns are sku, title, variant, quantity, unit, approved, source. Structured attributes are supported in JSON input.

## Difficult example

Two supplier rows share a SKU but have different pack sizes. Preserve both as exceptions; do not silently select one.

## Review evidence

Test on representative synthetic and approved merchant examples. Check imported columns, product facts, false claims, and correction effort. Publish one complete before/after example.
