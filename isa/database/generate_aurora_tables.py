from pathlib import Path
import json, csv, sys

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "aurora_v1_2_isa.json"

def validate(db):
    errors = []
    primaries = db["primary_opcode_map"]
    seen_mnemonics = set()
    for ins in db["instructions"]:
        if ins["mnemonic"] in seen_mnemonics:
            errors.append(f"duplicate mnemonic: {ins['mnemonic']}")
        seen_mnemonics.add(ins["mnemonic"])
        if ins["primary"] not in primaries:
            errors.append(f"bad primary opcode: {ins['mnemonic']}")
        if ins["latency"] < 1 or ins["initiation_interval"] < 1:
            errors.append(f"bad timing: {ins['mnemonic']}")
    return errors

def main():
    db = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate(db)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(db['instructions'])} instruction definitions.")
    print(f"Architecture: {db['architecture']} v{db['architecture_version']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
