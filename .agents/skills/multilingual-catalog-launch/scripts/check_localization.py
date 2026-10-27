"""Check product identity, protected facts, placeholders, and source revisions after localization."""
import re
from skill_io import index, rows, run


def placeholders(text):
    return sorted(re.findall(r"\{[^{}]+\}|%\([^)]+\)[a-z]|https?://[^\s]+", text))


def process(data):
    sources = index(data.get("source", []), "sku")
    targets = rows(data.get("localized", []), "localized")
    index(targets, "sku")
    output, issues = [], []
    seen = set()
    for item in targets:
        sku = str(item["sku"])
        seen.add(sku)
        source = sources.get(sku)
        codes = []
        if not source:
            codes.append("unknown_sku")
        else:
            if item.get("source_revision") != source.get("revision"):
                codes.append("stale_source_revision")
            if item.get("facts") != source.get("facts"):
                codes.append("protected_facts_changed")
            if item.get("variant_id") != source.get("variant_id"):
                codes.append("variant_changed")
            if placeholders(str(item.get("description", ""))) != placeholders(str(source.get("description", ""))):
                codes.append("protected_spans_changed")
        if item.get("locale") != data.get("target_locale"):
            codes.append("wrong_locale")
        if not str(item.get("title", "")).strip() or not str(item.get("description", "")).strip():
            codes.append("missing_copy")
        for code in codes:
            issues.append({"sku": sku, "code": code})
        output.append({**item, "check_status": "needs_review" if codes else "structural_checks_passed"})
    for sku in sorted(set(sources) - seen):
        issues.append({"sku": sku, "code": "missing_translation"})
    return {"records": output, "issues": issues,
            "semantic_quality": "not_measured", "native_review_required": True,
            "note": "Unchanged facts metadata cannot prove translated prose preserves those facts; review both."}


if __name__ == "__main__":
    run(process, __doc__)
