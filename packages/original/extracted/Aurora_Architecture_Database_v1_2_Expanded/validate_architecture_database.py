from pathlib import Path
import json, sys

root = Path(__file__).resolve().parent
db = json.loads((root / "aurora_architecture_v1_2.json").read_text())

errors = []
assert db["architecture"]["name"] == "Aurora"
if len(db["registers"]) != 16:
    errors.append("Expected 16 architectural registers.")
if db["architecture"]["retirement"] != "in_order":
    errors.append("Retirement must be in order.")
if db["architecture"]["register_renaming"]:
    errors.append("Register renaming must remain disabled.")
if db["timers"]["countdown_channels"] != 1:
    errors.append("Exactly one countdown timer is required.")
if any(r["name"] == "FULL_DIVIDER" for r in db["resources"]):
    errors.append("Dedicated full divider is forbidden in v1.2.")
if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("Aurora architecture database validation passed.")
