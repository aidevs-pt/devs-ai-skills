"""Complete the supplied price-update SOP example without changing live prices."""
from skill_io import index, number, run


def process(data):
    current = index(data.get("current", []), "sku")
    proposed = index(data.get("supplier", []), "sku")
    changes, exceptions = [], []
    for sku, row in proposed.items():
        old = current.get(sku)
        if not old:
            exceptions.append({"sku": sku, "code": "unknown_sku"})
            continue
        if not row.get("currency") or row.get("currency") != old.get("currency"):
            exceptions.append({"sku": sku, "code": "currency_mismatch"})
            continue
        before = number(old.get("price"), "current price", 0)
        after = number(row.get("price"), "supplier price", 0)
        if before != after:
            changes.append({"sku": sku, "old_price": str(before), "new_price": str(after),
                            "change_percent": str(((after - before) / before * 100).quantize(number("0.01"))) if before else None,
                            "currency": row["currency"], "status": "review_before_update"})
    return {"changes": changes, "exceptions": exceptions, "live_prices_changed": False}


if __name__ == "__main__":
    run(process, __doc__)
