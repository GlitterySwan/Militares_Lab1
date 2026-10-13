"""Small illustrative food database (values per 100 g, approximate).
In a real deployment, replace with USDA FoodData Central or the hospital's menu system."""

def f(kcal, carbs, sugar, fiber, protein, fat, sat, sodium, *tags, name=""):
    return dict(name=name, tags=list(tags), kcal=kcal, carbs_g=carbs, sugar_g=sugar, fiber_g=fiber,
                protein_g=protein, fat_g=fat, sat_fat_g=sat, sodium_mg=sodium)

FOODS = {
    "oatmeal_cooked":   f(71, 12, 0.3, 1.7, 2.5, 1.5, 0.3, 4,   "grain", "whole_grain", name="Oatmeal, cooked"),
    "white_rice":       f(130, 28, 0.1, 0.4, 2.7, 0.3, 0.1, 1,  "grain", name="White rice, cooked"),
    "brown_rice":       f(123, 26, 0.4, 1.6, 2.7, 1.0, 0.2, 4,  "grain", "whole_grain", name="Brown rice, cooked"),
    "whole_wheat_bread":f(252, 43, 6, 7, 12, 3.5, 0.8, 450,     "grain", "whole_grain", name="Whole wheat bread"),
    "white_bread":      f(266, 49, 5, 2.7, 9, 3.3, 0.7, 490,    "grain", name="White bread"),
    "egg_boiled":       f(155, 1.1, 1.1, 0, 13, 11, 3.3, 124,   "protein", name="Egg, boiled"),
    "chicken_breast":   f(165, 0, 0, 0, 31, 3.6, 1.0, 74,       "protein", name="Chicken breast, roasted"),
    "salmon_baked":     f(206, 0, 0, 0, 22, 12, 2.5, 61,        "protein", "fish", name="Salmon, baked"),
    "lentils_cooked":   f(116, 20, 1.8, 7.9, 9, 0.4, 0.1, 2,    "protein", "legume", name="Lentils, cooked"),
    "bacon":            f(541, 1.4, 0, 0, 37, 42, 14, 1717,     "processed_meat", "protein", name="Bacon"),
    "ham_deli":         f(107, 1.5, 1, 0, 17, 3.5, 1.2, 1200,   "processed_meat", "protein", name="Deli ham"),
    "canned_soup":      f(40, 6, 1.5, 1, 2, 1, 0.3, 480,        "high_sodium", name="Canned chicken noodle soup"),
    "broccoli_steamed": f(35, 7, 1.4, 3.3, 2.4, 0.4, 0.1, 41,   "vegetable", name="Broccoli, steamed"),
    "spinach_raw":      f(23, 3.6, 0.4, 2.2, 2.9, 0.4, 0.1, 79, "vegetable", name="Spinach, raw"),
    "carrots_cooked":   f(35, 8, 3.5, 3, 0.8, 0.2, 0, 58,       "vegetable", name="Carrots, cooked"),
    "apple":            f(52, 14, 10, 2.4, 0.3, 0.2, 0, 1,      "fruit", name="Apple"),
    "banana":           f(89, 23, 12, 2.6, 1.1, 0.3, 0.1, 1,    "fruit", name="Banana"),
    "orange_juice":     f(45, 10, 8.4, 0.2, 0.7, 0.2, 0, 1,     "fruit_juice", "sugary_drink", name="Orange juice"),
    "cola":             f(42, 10.6, 10.6, 0, 0, 0, 0, 4,        "sugary_drink", name="Cola"),
    "milk_lowfat":      f(42, 5, 5, 0, 3.4, 1, 0.6, 44,         "dairy", name="Milk, 1%"),
    "yogurt_plain":     f(61, 4.7, 4.7, 0, 3.5, 3.3, 2.1, 46,   "dairy", name="Yogurt, plain"),
    "cheddar":          f(403, 1.3, 0.5, 0, 25, 33, 21, 621,    "dairy", name="Cheddar cheese"),
    "olive_oil":        f(884, 0, 0, 0, 0, 100, 14, 2,          "fat", name="Olive oil"),
    "chocolate_cake":   f(371, 53, 36, 1.5, 4, 16, 6, 330,      "dessert", "sweets", name="Chocolate cake"),
    "pizza_slice":      f(266, 33, 3.6, 2.3, 11, 10, 4.5, 598,  "high_sodium", name="Pizza"),
    "almonds":          f(579, 22, 4.4, 12.5, 21, 50, 3.8, 1,   "nut", name="Almonds"),
}
for k, v in FOODS.items():
    v["id"] = k
