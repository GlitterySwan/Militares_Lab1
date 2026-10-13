"""Data models: policies/rules (the codified policy) and meal plans (the input)."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

NUTRIENTS = ["kcal", "carbs_g", "sugar_g", "fiber_g", "protein_g", "fat_g", "sat_fat_g", "sodium_mg"]
MealType = Literal["breakfast", "lunch", "dinner", "snack"]
KCAL_PER_G = {"sat_fat_g": 9, "fat_g": 9, "carbs_g": 4, "sugar_g": 4, "protein_g": 4}


# ---------- Policy side ----------
class Rule(BaseModel):
    id: str
    title: str
    # day  = evaluated on each day's totals
    # meal = evaluated on each meal's totals (optionally limited by meal_types)
    # item = evaluated on each individual food item
    scope: Literal["day", "meal", "item"]
    type: Literal[
        "nutrient_max",       # total of `nutrient` <= max
        "nutrient_min",       # total of `nutrient` >= min
        "nutrient_range",     # min <= total <= max
        "pct_kcal_max",       # (nutrient kcal / total kcal) * 100 <= max
        "per_1000kcal_min",   # nutrient per 1000 kcal >= min (e.g. fibre)
        "tag_forbidden",      # no item may carry any tag in `tags`
        "tag_min_grams",      # grams of items carrying any tag in `tags` >= min
    ]
    nutrient: Optional[str] = None
    tags: list[str] = []
    min: Optional[float] = None
    max: Optional[float] = None
    meal_types: Optional[list[MealType]] = None
    severity: Literal["error", "warning"] = "error"
    source: str = ""        # citation / policy clause -> evidence trail
    remedy: str = ""        # actionable guidance for the dietitian


class Policy(BaseModel):
    id: str
    name: str
    version: str
    description: str = ""
    rules: list[Rule]


# ---------- Input side ----------
class CustomFood(BaseModel):
    """Nutrients per 100 g, for foods not in the built-in database."""
    name: str
    tags: list[str] = []
    kcal: float = 0
    carbs_g: float = 0
    sugar_g: float = 0
    fiber_g: float = 0
    protein_g: float = 0
    fat_g: float = 0
    sat_fat_g: float = 0
    sodium_mg: float = 0


class Item(BaseModel):
    food_id: Optional[str] = None
    custom: Optional[CustomFood] = None
    grams: float = Field(gt=0)


class Meal(BaseModel):
    type: MealType
    items: list[Item]


class Day(BaseModel):
    label: str = "Day 1"
    meals: list[Meal]


class MealPlan(BaseModel):
    patient_ref: str = "anonymous"
    days: list[Day]


class ValidateRequest(BaseModel):
    policy_ids: list[str]
    plan: MealPlan
