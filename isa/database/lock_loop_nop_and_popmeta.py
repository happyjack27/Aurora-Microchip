"""
One-off script: lock in the LOOP/NOP hardware-loop encoding (ADR-ISA-020 /
ADR-FE-006) and allocate a real opcode for POPMETA (ADR-STREAM-009), then
regenerate the YAML/CSV mirrors so all four canonical files stay in sync.

- LOOPSET (0xC0) -> LOOP: format LOOP_IMM8, #count operand (1-256, encoded
  as count_minus_one). LOOPEND (0xC1) -> NOP: format LOOP_IMM8, no operand,
  terminates an active hardware loop. AGUCFG (0xC2) / STRIDE (0xC3) are left
  untouched - still an open question, see OPEN_QUESTIONS_CURRENT.md item 2.
- POPMETA is newly added at 0xB9 (format STREAM_POPMETA, new): Rd:Rd+1, Qn,
  meta aligned-pair stream consume-with-metadata, per ADR-STREAM-009.
"""
import json
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
from add_operand_columns import write_yaml, write_csv, CSV_PATH, DOCS_CSV_PATH  # noqa: E402

JSON_PATH = os.path.join(_DIR, "aurora_v1_2_isa.json")

POPMETA_INSTR = {
    "mnemonic": "POPMETA",
    "primary": "0xB",
    "subop": 9,
    "format": "STREAM_POPMETA",
    "operands": ["Rd:Rd+1", "Qn", "meta"],
    "operand_count": 3,
    "immediate_bits": 2,
    "semantics": "Rd = pop Qn; Rd+1 = selected metadata (ORD_LAST or ADDR_LAST)",
    "modes": ["SCALAR32", "PACKED16", "PACKED8", "PAIRED64"],
    "issue_slot": "B",
    "latency": 2,
    "initiation_interval": 1,
    "flags": [],
    "exceptions": [],
    "attributes": ["stream_state", "scoreboarded", "register_pair_dest"],
    "aliases": [],
}


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    instructions = data["instructions"]
    by_mnemonic = {i["mnemonic"]: i for i in instructions}

    loop = by_mnemonic["LOOPSET"]
    loop["mnemonic"] = "LOOP"
    loop["format"] = "LOOP_IMM8"
    loop["operands"] = ["#count"]
    loop["operand_count"] = 1
    loop["immediate_bits"] = 8
    loop["semantics"] = "Repeat the next 1-4 instructions count times; terminated by the first NOP (ADR-ISA-020)"
    loop["exceptions"] = ["LOOP_FORMAT"]

    nop = by_mnemonic["LOOPEND"]
    nop["mnemonic"] = "NOP"
    nop["format"] = "LOOP_IMM8"
    nop["operands"] = []
    nop["operand_count"] = 0
    nop["immediate_bits"] = 0
    nop["semantics"] = "No effect outside an active hardware loop; terminates the loop body when one is active"
    nop["exceptions"] = []

    # Insert POPMETA right after QSTEP (last STREAM entry) to keep primary-opcode ordering.
    qstep_idx = next(i for i, instr in enumerate(instructions) if instr["mnemonic"] == "QSTEP")
    instructions.insert(qstep_idx + 1, POPMETA_INSTR)

    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    write_yaml(data)
    write_csv(CSV_PATH, data)
    write_csv(DOCS_CSV_PATH, data)
    print(f"Locked LOOP/NOP (0xC0/0xC1) and added POPMETA (0xB9). Total instructions: {len(instructions)}.")


if __name__ == "__main__":
    main()
