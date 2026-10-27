# Business rules

- This is seller-side incoming customer order entry, not purchasing or supplier selection.

- An exact alias that resolves to multiple SKUs is ambiguous.

- Use Decimal quantities; do not silently round pieces or invent a pack size.

- Input duplicate order or line IDs are invalid; investigate rather than silently merging them.

## Difficult example

An alias matches two tray variants. Return both candidate codes for review, with no confirmed tray line.

## Review evidence

Test reviewed examples with unknown product codes, unit conversions, duplicates, and incomplete customer details. Measure errors accepted into the draft as well as extraction accuracy.
