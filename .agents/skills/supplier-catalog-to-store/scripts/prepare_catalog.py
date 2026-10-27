"""Prepare reviewable product data and safe import CSVs from approved supplier facts."""
import csv
import io
from collections import Counter
from pathlib import Path
from skill_io import csv_cell, number, rows, run


def process(data):
    products = data.get("products")
    if "supplier_csv" in data:
        with Path(data["supplier_csv"]).open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError("CSV needs unique column headers")
            products = list(reader)
    products = rows(products, "products")
    counts = Counter(str(p.get("sku", "")).strip() for p in products)
    output, issues = [], []
    for position, item in enumerate(products, 1):
        sku = str(item.get("sku", "")).strip()
        title = str(item.get("title", "")).strip()
        problems = []
        if not sku or not title:
            problems.append("missing_sku_or_title")
        if counts[sku] > 1:
            problems.append("duplicate_sku")
        quantity = item.get("quantity", "")
        if quantity != "":
            try:
                quantity = str(number(quantity, "quantity", 0))
                if number(quantity) == 0:
                    problems.append("zero_quantity")
            except ValueError:
                problems.append("invalid_quantity")
        unit = str(item.get("unit", "")).strip()
        if quantity != "" and not unit:
            problems.append("missing_quantity_unit")
        approved = item.get("approved") in (True, "true", "TRUE", "1")
        if not approved:
            problems.append("source_not_approved")
        attributes = item.get("attributes", {})
        if not isinstance(attributes, dict):
            raise ValueError("attributes must be an object")
        facts = []
        if quantity != "" and "invalid_quantity" not in problems:
            facts.append(f"{quantity} {unit}".strip())
        facts.extend(f"{key}: {value}" for key, value in sorted(attributes.items()) if value is not None)
        source = str(item.get("source", ""))
        if not source:
            problems.append("missing_source_reference")
        for problem in problems:
            issues.append({"row": position, "sku": sku, "code": problem, "source": source})
        record = {"sku": sku, "title": title, "variant": str(item.get("variant", "")),
                  "quantity": quantity, "unit": unit, "source": source,
                  "facts": attributes, "status": "needs_review" if problems else "draft_ready",
                  "draft_description": title + (". " + "; ".join(facts) + "." if facts else ".")}
        output.append(record)
    text = io.StringIO(newline="")
    writer = csv.writer(text, lineterminator="\n")
    writer.writerow(["sku", "title", "variant", "description", "source", "status"])
    for item in output:
        writer.writerow([csv_cell(item[k]) for k in ["sku", "title", "variant", "draft_description", "source", "status"]])
    return {"records": output, "issues": issues, "import_csv": text.getvalue(),
            "review_required": True, "semantic_review": "Host agent must review claims; no semantic accuracy score is computed."}


if __name__ == "__main__":
    run(process, __doc__)
