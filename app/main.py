from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from .engine import load_policies, validate_against
from .foods import FOODS
from .models import ValidateRequest

app = FastAPI(title="Diet Policy Compliance Engine", version="1.1")
POLICIES = load_policies()
INDEX = Path(__file__).parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(INDEX)          # the GUI


@app.get("/policies")
def list_policies():
    return [{"id": p.id, "name": p.name, "version": p.version, "rule_count": len(p.rules)} for p in POLICIES.values()]


@app.get("/policies/{policy_id}")
def get_policy(policy_id: str):
    if policy_id not in POLICIES:
        raise HTTPException(404, f"Unknown policy '{policy_id}'")
    return POLICIES[policy_id]


@app.get("/foods")
def list_foods():
    return list(FOODS.values())


@app.post("/validate")
def validate(req: ValidateRequest):
    try:
        return validate_against(req.policy_ids, req.plan, POLICIES)
    except KeyError as e:
        raise HTTPException(404, f"Unknown policy id(s): {e.args[0]}")
    except ValueError as e:
        raise HTTPException(422, str(e))