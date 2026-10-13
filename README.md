# Diet Policy Compliance Engine

Rule-based validator that checks meal plans against codified dietary policies
(low-sodium, consistent-carbohydrate/diabetic). **Policies are data (JSON), the engine is generic code.**
Adding or amending a policy never requires changing Python.

## Run
```bash
pip install -r requirements.txt
pytest -q                          # unit tests
uvicorn app.main:app --reload      # API at http://127.0.0.1:8000/docs
curl -X POST localhost:8000/validate -H "Content-Type: application/json" -d @sample_request.json
```

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/policies`, `/policies/{id}` | List / inspect codified policies |
| GET | `/foods` | Built-in food database |
| POST | `/validate` | Validate a plan against one or more policies |

## Architecture
```
policies/*.json  -> Policy{ Rule[] }   (id, scope, type, thresholds, severity, source, remedy)
meal plan (JSON) -> resolve foods -> totals per item / meal / day
engine.evaluate  -> for each rule + scope -> pass/fail -> violations (with evidence + remedy)
```
Rule scopes: `day`, `meal` (optionally filtered by meal type), `item`.
Rule types: `nutrient_max|min|range`, `pct_kcal_max`, `per_1000kcal_min`, `tag_forbidden`, `tag_min_grams`.

## Output
`compliant` is false only when an **error**-severity rule fails; **warnings** are advisory.
Every violation carries the rule id, where it occurred, actual vs limit, the policy `source`, and a `remedy`.

## Caveat
Thresholds and food values are illustrative for coursework. A real deployment must use the institution's
current diet manual and a validated food database (e.g. USDA FoodData Central), and be signed off by a registered dietitian.
