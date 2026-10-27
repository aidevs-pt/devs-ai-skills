"""Match incoming customer PO lines to approved catalog codes without submitting orders."""
from collections import defaultdict
from skill_io import index, number, rows, run


def process(data):
    products = index(data.get("catalog", []), "sku")
    aliases = defaultdict(set)
    for sku, product in products.items():
        if not isinstance(product.get("aliases", []), list) or any(not isinstance(x, str) for x in product.get("aliases", [])):
            raise ValueError("aliases must be an array of strings")
        if not isinstance(product.get("unit"), str) or not product["unit"]:
            raise ValueError("Catalog products need an explicit base unit")
        for code in [sku, *product.get("aliases", [])]:
            aliases[str(code).strip().casefold()].add(sku)
    orders = rows(data.get("orders", []), "orders")
    index(orders)
    drafts = []
    for order in orders:
        output, exceptions = [], []
        lines = rows(order.get("lines", []), "lines")
        index(lines)
        if not order.get("customer_id"):
            exceptions.append({"code": "missing_customer_id"})
        for line in lines:
            key = str(line.get("product_code", "")).strip().casefold()
            matches = sorted(aliases.get(key, set()))
            issue = None
            if len(matches) != 1:
                issue = "unknown_product" if not matches else "ambiguous_product"
            else:
                product = products[matches[0]]
                try:
                    quantity = number(line.get("quantity"), "quantity", 0)
                    if quantity == 0:
                        raise ValueError("Quantity must be positive")
                    unit = line.get("unit")
                    if unit != product.get("unit"):
                        conversions = product.get("unit_conversions", {})
                        if unit not in conversions:
                            issue = "unknown_unit_conversion"
                        else:
                            quantity *= number(conversions[unit], "conversion", 0)
                            if quantity <= 0:
                                raise ValueError("Conversion must be positive")
                except ValueError:
                    issue = "invalid_quantity_or_conversion"
                if not issue:
                    output.append({"line_id": line["id"], "sku": matches[0], "quantity": str(quantity),
                                   "unit": product["unit"], "source": line.get("source"),
                                   "catalog_source": product.get("source"), "status": "draft"})
            if issue:
                exceptions.append({"line_id": line["id"], "code": issue, "candidates": matches, "source": line.get("source")})
        drafts.append({"order_id": order["id"], "customer_id": order.get("customer_id"),
                       "lines": output, "exceptions": exceptions,
                       "status": "draft_incomplete" if exceptions else "draft_ready_for_review"})
    return {"orders": drafts, "submitted": False}


if __name__ == "__main__":
    run(process, __doc__)
