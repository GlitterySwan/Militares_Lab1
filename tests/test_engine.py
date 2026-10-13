from app.engine import load_policies, validate_against
from app.models import MealPlan

POL = load_policies()

def plan(meals, label="Day 1"):
    return MealPlan.model_validate({"days": [{"label": label, "meals": meals}]})

def m(type_, *items):
    return {"type": type_, "items": [{"food_id": f, "grams": g} for f, g in items]}

def ids(result, kind="errors"):
    return {v["rule_id"] for r in result["results"] for v in r[kind]}

GOOD_LOW_NA = plan([
    m("breakfast", ("oatmeal_cooked", 250), ("banana", 100)),
    m("lunch", ("chicken_breast", 120), ("brown_rice", 150), ("broccoli_steamed", 150)),
    m("dinner", ("salmon_baked", 120), ("carrots_cooked", 120), ("spinach_raw", 80)),
])

def test_low_sodium_compliant_plan_passes():
    r = validate_against(["low_sodium"], GOOD_LOW_NA, POL)
    assert r["overall_compliant"], r

def test_bacon_and_soup_trigger_violations():
    p = plan([m("breakfast", ("bacon", 100), ("egg_boiled", 100)),
              m("lunch", ("canned_soup", 400), ("ham_deli", 100)),
              m("dinner", ("pizza_slice", 200))])
    r = validate_against(["low_sodium"], p, POL)
    assert {"NA-DAY-MAX", "NA-ITEM-PROC"} <= ids(r)
    assert "NA-ITEM-HIGHNA" in ids(r, "warnings")
    assert not r["overall_compliant"]

def test_diabetic_carb_range_and_ssb():
    p = plan([m("breakfast", ("oatmeal_cooked", 250), ("orange_juice", 250)),   # 30+25 carbs -> 55 but juice is banned
              m("lunch", ("white_rice", 300)),                                  # 84 g carbs -> too high
              m("dinner", ("chicken_breast", 150), ("broccoli_steamed", 100))])  # ~7 g carbs -> too low
    r = validate_against(["diabetic"], p, POL)
    errs = ids(r)
    assert "DM-ITEM-SSB" in errs
    assert "DM-MEAL-CARB" in errs
    carb = [v for v in r["results"][0]["errors"] if v["rule_id"] == "DM-MEAL-CARB"]
    assert {v["location"] for v in carb} == {"lunch", "dinner"}

def test_snack_scope_only_applies_to_snacks():
    p = plan([m("snack", ("chocolate_cake", 100))])  # 53 g carbs in a snack
    r = validate_against(["diabetic"], p, POL)
    assert "DM-SNACK-CARB" in ids(r)
    assert "DM-MEAL-CARB" not in ids(r)

def test_multi_policy_and_custom_food():
    p = MealPlan.model_validate({"days": [{"meals": [
        {"type": "lunch", "items": [{"custom": {"name": "Hospital stew", "kcal": 90, "carbs_g": 10,
                                                 "sodium_mg": 900, "tags": []}, "grams": 400}]}]}]})
    r = validate_against(["low_sodium", "diabetic"], p, POL)
    assert len(r["results"]) == 2
    assert "NA-DAY-MAX" in ids(r)   # 3,600 mg sodium

def test_unknown_policy_raises():
    import pytest
    with pytest.raises(KeyError):
        validate_against(["nope"], GOOD_LOW_NA, POL)
