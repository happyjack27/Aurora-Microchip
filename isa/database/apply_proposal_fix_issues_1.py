"""
One-off script: implement "Resolve Aurora v1.2 ISA Reconciliation Questions"
(proposals/fix issues 1.txt), covering the DB-level decisions:

- Retire AGUCFG (0xC2) / STRIDE (0xC3): removed entirely (no ADR ever backed
  them; superseded by the fuller AUR-ARCH-004 AGU class which itself was
  never adopted - see OPEN_QUESTIONS_CURRENT.md item 2, now closed).
- Allocate LOOPR at 0xC2 (format LOOP_REG, new): register-supplied loop
  count, same NOP-terminated body machinery as LOOP. Per ADR-ISA-022.
- 0xC3-0xC9 remain reserved (no DB entries - unused opcodes are implicit).
- MAC/MAS operand 0 changes from a bare "dst" GPR placeholder to
  "accumulator" (selector), matching the semantics (`A = A +/- Ra*Rb`)
  which never referenced a GPR destination. Per ADR-DSP-018.
- Add operand_spec_confidence / encoding_spec_confidence /
  semantic_spec_confidence / sources / notes to every instruction, derived
  mechanically from aurora_v1_2_encoding.json format status and from
  whether `semantics`/`operands` are still generic placeholder text.
"""
import json
import os
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
from add_operand_columns import write_yaml, write_csv, CSV_PATH, DOCS_CSV_PATH  # noqa: E402

JSON_PATH = os.path.join(_DIR, "aurora_v1_2_isa.json")
ENCODING_PATH = os.path.join(_DIR, "aurora_v1_2_encoding.json")

LOOPR_INSTR = {
    "mnemonic": "LOOPR",
    "primary": "0xC",
    "subop": 2,
    "format": "LOOP_REG",
    "operands": ["Rs"],
    "operand_count": 1,
    "immediate_bits": 0,
    "semantics": "Repeat the next 1-4 instructions Rs times (unsigned, must be nonzero); terminated by the first NOP (ADR-ISA-022)",
    "modes": ["SCALAR32"],
    "issue_slot": "A",
    "latency": 1,
    "initiation_interval": 1,
    "flags": [],
    "exceptions": ["LOOP_FORMAT"],
    "attributes": ["control_barrier"],
    "aliases": [],
}

# Extra ADR references appended to the mechanically-derived `sources` list.
EXTRA_SOURCES = {
    "LOOP": ["ADR-ISA-020"],
    "NOP": ["ADR-ISA-020"],
    "LOOPR": ["ADR-ISA-022"],
    "POPMETA": ["ADR-STREAM-009"],
    "MAC": ["ADR-DSP-018"],
    "MAS": ["ADR-DSP-018"],
}

_STUB_RE = re.compile(r"^\S+ (system operation|stream/queue operation|low-overhead loop or address-generation control)$")


def confidence_for(instr, fmt_status):
    is_stub_semantics = bool(_STUB_RE.match(instr["semantics"]))
    is_stub_operands = instr["operands"] == ["args"]
    documented = fmt_status == "normative"

    encoding_spec_confidence = "documented" if documented else "inferred"
    operand_spec_confidence = "unresolved" if is_stub_operands else ("documented" if documented else "inferred")
    semantic_spec_confidence = "unresolved" if is_stub_semantics else ("documented" if documented else "inferred")

    notes = []
    if is_stub_operands:
        notes.append("operands field is a placeholder ('args'); real operand roles not itemized")
    if is_stub_semantics:
        notes.append("semantics field restates the mnemonic name only; behavior not documented")
    return operand_spec_confidence, encoding_spec_confidence, semantic_spec_confidence, "; ".join(notes)


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(ENCODING_PATH, "r", encoding="utf-8") as f:
        encoding = json.load(f)
    formats = encoding["formats"]

    instructions = data["instructions"]
    by_mnemonic = {i["mnemonic"]: i for i in instructions}

    # --- Retire AGUCFG / STRIDE ---
    instructions[:] = [i for i in instructions if i["mnemonic"] not in ("AGUCFG", "STRIDE")]

    # --- Allocate LOOPR at 0xC2 (right after NOP) ---
    nop_idx = next(i for i, instr in enumerate(instructions) if instr["mnemonic"] == "NOP")
    instructions.insert(nop_idx + 1, LOOPR_INSTR)

    # --- MAC/MAS operand 0: dst -> accumulator ---
    for mnemonic in ("MAC", "MAS"):
        instr = by_mnemonic[mnemonic]
        instr["operands"] = ["accumulator" if o == "dst" else o for o in instr["operands"]]

    # --- Confidence / provenance metadata ---
    for instr in instructions:
        fmt = formats.get(instr["format"], {})
        op_conf, enc_conf, sem_conf, notes = confidence_for(instr, fmt.get("status"))
        sources = []
        if fmt.get("source"):
            sources.append(fmt["source"])
        sources.extend(EXTRA_SOURCES.get(instr["mnemonic"], []))
        instr["operand_spec_confidence"] = op_conf
        instr["encoding_spec_confidence"] = enc_conf
        instr["semantic_spec_confidence"] = sem_conf
        instr["sources"] = sources
        instr["notes"] = notes

    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    write_yaml(data)
    write_csv(CSV_PATH, data)
    write_csv(DOCS_CSV_PATH, data)
    print(f"Retired AGUCFG/STRIDE, added LOOPR, fixed MAC/MAS operand, added confidence metadata. "
          f"Total instructions: {len(instructions)}.")


if __name__ == "__main__":
    main()
