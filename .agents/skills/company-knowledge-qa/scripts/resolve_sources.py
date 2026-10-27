"""Resolve dated, scoped document evidence and surface conflicts before answering."""
from collections import defaultdict
from datetime import date
import re
from skill_io import index, rows, run

STOP = {'a','an','and','are','be','can','do','for','from','how','in','is','it','of','on','or','our','the','to','we','what','when','which','with'}


def process(data):
    as_of = date.fromisoformat(data["as_of"])
    scope = data["scope"]
    documents = rows(data.get("documents", []), "documents")
    by_id = index(documents)
    groups, manifest, issues = defaultdict(list), [], []
    for doc in documents:
        key = str(doc["id"])
        reasons = []
        if doc.get("approved") is not True:
            reasons.append("unapproved")
        if doc.get("scope") not in (scope, "all"):
            reasons.append("outside_requested_scope")
        if not doc.get("effective_from"):
            reasons.append("unknown_effective_date")
        elif date.fromisoformat(doc["effective_from"]) > as_of:
            reasons.append("not_yet_effective")
        if doc.get("effective_to") and date.fromisoformat(doc["effective_to"]) < as_of:
            reasons.append("expired")
        if not doc.get("owner"):
            issues.append({"source_id": key, "code": "missing_owner"})
        if not doc.get("topic") or not isinstance(doc.get("content"), str):
            reasons.append("missing_topic_or_content")
        manifest.append({"id": key, "owner": doc.get("owner"), "reasons": reasons, "eligible": not reasons})
        if not reasons:
            groups[doc["topic"]].append(doc)
    active, conflicts = [], []
    for topic, docs in groups.items():
        superseded = {str(x) for d in docs for x in d.get("supersedes", [])}
        eligible = [d for d in docs if str(d["id"]) not in superseded]
        if len({d["content"].strip() for d in eligible}) > 1:
            conflicts.append({"topic": topic, "sources": [d["id"] for d in eligible], "action": "ask_document_owner"})
        else:
            active.extend(eligible)
    candidates = []
    for question in data.get("questions", []):
        if not isinstance(question, str):
            raise ValueError("questions must contain strings")
        tokens = set(re.findall(r"\w+", question.casefold())) - STOP
        ranked = []
        for doc in active:
            score = len(tokens & set(re.findall(r"\w+", (doc["topic"] + " " + doc["content"]).casefold())))
            if score:
                ranked.append({"source_id": doc["id"], "matching_terms": score, "content": doc["content"]})
        ranked.sort(key=lambda x: (-x["matching_terms"], str(x["source_id"])))
        candidates.append({"question": question, "evidence": ranked[:5], "answer_status": "needs_cited_answer" if ranked else "insufficient_evidence"})
    return {"as_of": as_of.isoformat(), "scope": scope, "source_manifest": manifest,
            "conflicts": conflicts, "issues": issues, "questions": candidates,
            "note": "File scope filtering is not deployed authorization. Lexical candidates are not verified answers."}


if __name__ == "__main__":
    run(process, __doc__)
