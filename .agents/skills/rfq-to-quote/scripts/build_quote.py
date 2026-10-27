"""Create a draft quote from explicit approved catalog prices using decimal arithmetic."""
from decimal import Decimal, ROUND_HALF_UP
from skill_io import index, number, rows, run


def money(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def process(data):
    catalog = index(data.get("catalog", []), "sku")
    lines = rows(data.get("request", []), "request")
    index(lines)
    currency = data.get("currency")
    if not isinstance(currency, str) or len(currency) != 3:
        raise ValueError("Supply a currency")
    output, exceptions, subtotal = [], [], Decimal(0)
    for line in lines:
        sku = str(line.get("sku", ""))
        product = catalog.get(sku)
        reason = None
        if not product:
            reason = "unknown_sku"
        elif product.get("approved") is not True or not product.get("price_source"):
            reason = "unapproved_or_unsourced_price"
        elif product.get("currency") != currency:
            reason = "currency_mismatch"
        else:
            try:
                quantity = number(line.get("quantity"), "quantity", 0)
                if quantity == 0:
                    raise ValueError("Quantity must be positive")
                price = number(product.get("unit_price"), "unit price", 0)
            except ValueError:
                reason = "invalid_quantity_or_price"
        if reason:
            exceptions.append({"line_id": line["id"], "sku": sku, "code": reason})
            continue
        total = (quantity * price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal += total
        output.append({"line_id": line["id"], "sku": sku, "quantity": str(quantity),
                       "unit_price": str(price), "line_total": money(total), "price_source": product["price_source"]})
    tax = None
    if "tax_rate" in data:
        if not data.get("tax_rule_source"):
            raise ValueError("An explicit tax rate also needs tax_rule_source")
        rate = number(data["tax_rate"], "tax_rate", 0)
        if rate > 1:
            raise ValueError("tax_rate must be a fraction between zero and one")
        tax = (subtotal * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    complete = not exceptions and bool(lines)
    return {"quote_id": data.get("quote_id"), "currency": currency, "lines": output,
            "exceptions": exceptions, "confirmed_lines_subtotal": money(subtotal),
            "tax": money(tax) if tax is not None else None,
            "total": money(subtotal + tax) if complete and tax is not None else None,
            "tax_status": "supplied_rule_applied" if tax is not None else "not_supplied",
            "status": "draft_ready_for_review" if complete else "draft_incomplete",
            "sent": False, "delivery_terms": data.get("approved_delivery_terms")}


if __name__ == "__main__":
    run(process, __doc__)
