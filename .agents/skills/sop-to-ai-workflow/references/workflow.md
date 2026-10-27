# Business rules

- A review node must precede an external action in the contract; actual authorization still requires a runtime decision.

- Name the input snapshot and transformation, so a repeated run can detect duplicate work.

- Do not claim a process is automated when the assistant only drew a diagram.

- Unknown prices/currencies remain exceptions; price updates use supplied values only.

## Difficult example

A workflow writes to a live system without any review ancestor. Flag the missing boundary and do not execute the action.

## Review evidence

Use procedures with clear inputs and outputs. Compare the completed sample with a reviewed reference and check whether a second person can repeat the run.
