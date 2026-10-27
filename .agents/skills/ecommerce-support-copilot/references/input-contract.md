# Input contract

tickets/orders/policies are arrays with unique id strings. Ticket order_id and customer_id must match an order. Policies need approved=true and matching region. intent is supplied by the host, not inferred by this helper.

Use [the synthetic example](../assets/example-input.json) as an exact field-name example.
All dates and commercial rules are supplied by the operator. No default legal, tax,
delivery, or business policy is implied. Unknown facts remain explicit.

The helper accepts `--input`, optional `--output`, and `--overwrite`.
Exit 0 means the analysis completed; the report may still contain exceptions.
Exit 2 means invalid input or an output error. Inspect the JSON review state before use.

## Output contract

ticket_id | intent | verified facts | draft reply | next action | source handles | review state

Helper JSON is an intermediate evidence object. The host must produce the actual
requested business artifact using the workflow and output template. Preserve record IDs.
