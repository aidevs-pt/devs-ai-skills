"""Check a bounded workflow contract for missing inputs, cycles, and review boundaries."""
from skill_io import index, rows, run


def process(data):
    steps = rows(data.get("steps", []), "steps")
    by_id = index(steps)
    external = set(data.get("supplied_inputs", []))
    producers, issues = {}, []
    for step in steps:
        if step.get("type") not in ("manual", "rule", "ai", "review", "external_action"):
            raise ValueError("Step type must be manual, rule, ai, review, or external_action")
        for field in ("inputs", "outputs", "depends_on"):
            if not isinstance(step.get(field, []), list) or any(not isinstance(x, str) for x in step.get(field, [])):
                raise ValueError(f"{field} must be an array of strings")
        for output in step.get("outputs", []):
            if output in producers or output in external:
                issues.append({"step": step["id"], "code": "duplicate_output", "name": output})
            producers[output] = step["id"]
    graph = {}
    for step in steps:
        dependencies = set(step.get("depends_on", []))
        for name in step.get("inputs", []):
            if name in producers:
                dependencies.add(producers[name])
            elif name not in external:
                issues.append({"step": step["id"], "code": "missing_input", "name": name})
        for dependency in dependencies:
            if dependency not in by_id:
                issues.append({"step": step["id"], "code": "unknown_dependency", "name": dependency})
        graph[step["id"]] = dependencies
    visiting, done, cyclic = set(), set(), set()

    def visit(key):
        if key in visiting:
            cyclic.add(key)
            return
        if key in done or key not in graph:
            return
        visiting.add(key)
        for parent in graph[key]:
            visit(parent)
        visiting.remove(key)
        done.add(key)

    for key in graph:
        visit(key)
    if cyclic:
        issues.append({"code": "dependency_cycle", "steps": sorted(cyclic)})

    def ancestors(key, seen=None):
        seen = set() if seen is None else seen
        for parent in graph.get(key, set()):
            if parent not in seen:
                seen.add(parent)
                ancestors(parent, seen)
        return seen

    for step in steps:
        if step["type"] == "external_action":
            reviews = [x for x in ancestors(step["id"]) if by_id.get(x, {}).get("type") == "review"]
            if not reviews:
                issues.append({"step": step["id"], "code": "external_action_without_review"})
        if step["type"] == "ai" and not step.get("acceptance_check"):
            issues.append({"step": step["id"], "code": "missing_acceptance_check"})
    return {"name": data.get("name"), "issues": issues, "contract_valid": not issues,
            "executed_workflow": False, "note": "A valid contract does not prove a connector or runtime enforces it."}


if __name__ == "__main__":
    run(process, __doc__)
