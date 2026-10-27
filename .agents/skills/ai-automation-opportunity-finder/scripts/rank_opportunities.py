"""Calculate transparent scenario estimates from supplied process measurements."""
from decimal import Decimal
from skill_io import index, number, rows, run


def process(data):
    tasks = rows(data.get("tasks", []), "tasks")
    index(tasks)
    ranked, unknown = [], []
    for task in tasks:
        required = ["runs_per_month", "minutes_per_run", "automatable_fraction", "review_minutes_per_run"]
        missing = [key for key in required if task.get(key) is None]
        if missing:
            unknown.append({"id": task["id"], "missing": missing})
            continue
        runs = number(task["runs_per_month"], "runs_per_month", 0)
        before = number(task["minutes_per_run"], "minutes_per_run", 0)
        fraction = number(task["automatable_fraction"], "automatable_fraction", 0)
        review = number(task["review_minutes_per_run"], "review_minutes_per_run", 0)
        if fraction > 1:
            raise ValueError("automatable_fraction must be between zero and one")
        manual_hours = runs * before / Decimal(60)
        after_hours = runs * (before * (1 - fraction) + review) / Decimal(60)
        saved = manual_hours - after_hours
        amount = None
        if task.get("hourly_cost") is not None:
            amount = saved * number(task["hourly_cost"], "hourly_cost", 0)
        evidence = task.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("evidence must be an array")
        ranked.append({"id": task["id"], "manual_hours_per_month": str(manual_hours.quantize(Decimal("0.01"))),
                       "scenario_hours_per_month": str(after_hours.quantize(Decimal("0.01"))),
                       "scenario_hours_saved": str(saved.quantize(Decimal("0.01"))),
                       "scenario_labor_value": str(amount.quantize(Decimal("0.01"))) if amount is not None else None,
                       "currency": task.get("currency") if amount is not None else None,
                       "evidence": evidence, "evidence_status": "supplied" if evidence else "assumption_only",
                       "assumptions": {k: str(task[k]) for k in required},
                       "options_to_compare": ["process_change", "existing_software", "rules_automation", "ai_assisted_workflow"],
                       "net_roi": None})
    ranked.sort(key=lambda x: (-Decimal(x["scenario_hours_saved"]), str(x["id"])))
    return {"ranked_scenarios": ranked, "needs_more_information": unknown,
            "note": "Scenario estimates exclude unspecified software, implementation, monitoring, and maintenance costs. No guaranteed savings or ROI."}


if __name__ == "__main__":
    run(process, __doc__)
