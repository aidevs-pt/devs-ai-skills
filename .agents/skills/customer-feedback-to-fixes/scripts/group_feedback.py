"""Group explicitly labeled customer evidence with deduplication and traceable counts."""
from collections import defaultdict
import re
from skill_io import index, rows, run


def process(data):
    items = rows(data.get("items", []), "items")
    index(items)
    groups, duplicates, seen, unclassified = defaultdict(list), [], {}, []
    for item in items:
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Each feedback item needs non-empty text")
        normalized = re.sub(r"\s+", " ", text.strip().casefold())
        # Only deduplicate cross-record text when identity or a shared source proves a link.
        person = item.get("customer_id")
        shared = item.get("source_event_id")
        context = (str(item.get("product", "unknown")), str(item.get("journey_stage", "unknown")))
        signature = ("event", str(shared), normalized, *context) if shared else (("person", str(person), normalized, *context) if person else ("record", str(item["id"])))
        if signature in seen:
            duplicates.append({"id": item["id"], "duplicate_of": seen[signature]})
            continue
        seen[signature] = item["id"]
        theme = item.get("theme")
        if not theme:
            unclassified.append(item["id"])
            continue
        groups[(str(theme), str(item.get("product", "unknown")), str(item.get("journey_stage", "unknown")))].append(item)
    output = []
    for (theme, product, stage), evidence in sorted(groups.items()):
        known_people = {str(x["customer_id"]) for x in evidence if x.get("customer_id")}
        all_known = all(x.get("customer_id") for x in evidence)
        output.append({"theme": theme, "product": product, "journey_stage": stage,
                       "record_count": len(evidence), "known_unique_customers": len(known_people),
                       "total_unique_customers": len(known_people) if all_known else None,
                       "evidence": [{"id": x["id"], "quote": x["text"], "source": x.get("source")} for x in evidence],
                       "suggested_fix_status": "host_to_form_hypothesis_from_evidence"})
    return {"groups": output, "duplicates": duplicates, "unclassified": unclassified,
            "population_representativeness": "unknown", "sentiment_score": None}


if __name__ == "__main__":
    run(process, __doc__)
