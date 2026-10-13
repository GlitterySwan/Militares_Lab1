"""Rule engine: pure Python, no web dependencies, so it is trivially unit-testable."""
import json
from pathlib import Path
from .foods import FOODS
from .models import KCAL_PER_G, NUTRIENTS, MealPlan, Policy, Rule

POLICY_DIR = Path(__file__).resolve().parent.parent / "policies"


def load_policies(directory: Path = POLICY_DIR) -> dict[str, Policy]:
    policies = {}
    for path in sorted(directory.glob("*.json")):
        p = Policy.model_validate(json.loads(path.read_text()))
        policies[p.id] = p
    return policies


# ---------- Nutrient calculation ----------
def resolve_item(item) -> dict:
    """Return the item's actual nutrient contribution (scaled by grams) plus tags."""
    if item.custom:
        base, tags, name = item.custom.model_dump(), item.custom.tags, item.custom.name
    elif item.food_id in FOODS:
        base, tags, name = FOODS[item.food_id], FOODS[item.food_id]["tags"], FOODS[item.food_id]["name"]
    else:
        raise ValueError(f"Unknown food_id '{item.food_id}' and no custom food supplied")
    k = item.grams / 100
    out = {n: base[n] * k for n in NUTRIENTS}
    out.update(name=name, tags=list(tags), grams=item.grams)
    return out


def sum_items(items: list[dict]) -> dict:
    totals = {n: sum(i[n] for i in items) for n in NUTRIENTS}
    totals["items"] = items
    return totals


# ---------- Rule evaluation ----------
def _check(rule: Rule, totals: dict):
    """Evaluate one rule against one set of totals.
    Returns (passed, actual, limit_description)."""
    t = rule.type
    if t in ("nutrient_max", "nutrient_min", "nutrient_range"):
        actual = totals[rule.nutrient]
    elif t == "pct_kcal_max":
        actual = 0 if totals["kcal"] == 0 else totals[rule.nutrient] * KCAL_PER_G[rule.nutrient] / totals["kcal"] * 100
    elif t == "per_1000kcal_min":
        actual = 0 if totals["kcal"] == 0 else totals[rule.nutrient] / totals["kcal"] * 1000
    elif t == "tag_min_grams":
        actual = sum(i["grams"] for i in totals["items"] if set(i["tags"]) & set(rule.tags))
    else:
        raise ValueError(f"Unsupported rule type {t}")

    ok = True
    if rule.min is not None and actual < rule.min:
        ok = False
    if rule.max is not None and actual > rule.max:
        ok = False
    limit = {"min": rule.min, "max": rule.max}
    return ok, round(actual, 1), limit


def evaluate(policy: Policy, plan: MealPlan) -> dict:
    violations, checks = [], 0
    per_day = []

    for day in plan.days:
        meal_totals = [(m, sum_items([resolve_item(i) for i in m.items])) for m in day.meals]
        day_totals = sum_items([i for _, mt in meal_totals for i in mt["items"]])
        per_day.append({"day": day.label, "totals": {n: round(day_totals[n], 1) for n in NUTRIENTS}})

        def record(rule, location, ok, actual, limit, extra=""):
            if not ok:
                violations.append({
                    "rule_id": rule.id, "policy_id": policy.id, "title": rule.title,
                    "severity": rule.severity, "day": day.label, "location": location,
                    "actual": actual, "limit": limit, "detail": extra,
                    "source": rule.source, "remedy": rule.remedy,
                })

        for rule in policy.rules:
            if rule.scope == "day":
                checks += 1
                ok, actual, limit = _check(rule, day_totals) if rule.type != "tag_forbidden" else (True, 0, {})
                record(rule, "whole day", ok, actual, limit)

            elif rule.scope == "meal":
                for meal, mt in meal_totals:
                    if rule.meal_types and meal.type not in rule.meal_types:
                        continue
                    checks += 1
                    ok, actual, limit = _check(rule, mt)
                    record(rule, meal.type, ok, actual, limit)

            elif rule.scope == "item" and rule.type == "tag_forbidden":
                for meal, mt in meal_totals:
                    for it in mt["items"]:
                        checks += 1
                        hit = sorted(set(it["tags"]) & set(rule.tags))
                        record(rule, f"{meal.type}: {it['name']}", not hit, it["grams"], {"forbidden_tags": rule.tags},
                               f"Item carries forbidden tag(s): {', '.join(hit)}" if hit else "")

    errors = [v for v in violations if v["severity"] == "error"]
    warnings = [v for v in violations if v["severity"] == "warning"]
    return {
        "policy_id": policy.id, "policy_name": policy.name, "policy_version": policy.version,
        "compliant": not errors,
        "checks_run": checks,
        "compliance_score": round(100 * (checks - len(violations)) / checks, 1) if checks else 100.0,
        "errors": errors, "warnings": warnings,
        "daily_totals": per_day,
    }


def validate_against(policy_ids: list[str], plan: MealPlan, policies: dict[str, Policy]) -> dict:
    missing = [p for p in policy_ids if p not in policies]
    if missing:
        raise KeyError(missing)
    results = [evaluate(policies[p], plan) for p in policy_ids]
    return {
        "patient_ref": plan.patient_ref,
        "overall_compliant": all(r["compliant"] for r in results),
        "results": results,
    }
