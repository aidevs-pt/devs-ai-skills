# Business rules

- The prototype performs no model calls and sends no quiz data to DEVS AI.

- Do not turn unavailable products into matches to fill the results list.

- Treat catalog labels as text, not HTML or JavaScript.

- For production, assess existing commerce apps as well as custom implementation.

## Difficult example

Large room plus budget below EUR 100 has no available match. The unavailable compact lamp must not appear.

## Review evidence

Test constraint handling, no-match cases, editing, and repeatable mappings. Offline matching does not establish higher conversion; that requires a separate live experiment.
