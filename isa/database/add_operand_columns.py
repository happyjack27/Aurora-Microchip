"""
One-off script: add operand_count and immediate_bits columns to the Aurora
v1.2 instruction database (JSON source of truth), then regenerate the YAML
and both CSV mirrors from it so all four stay in sync.

operand_count = number of operands as WRITTEN in assembly syntax (2-address
forms like RRR count Rd and Ra separately even though they share one
physical bit field, matching the datasheet's own "ADD R1, R1, R2" example).

immediate_bits = width of the base-word immediate/control field for that
format (0 if the format is register-only). Where a mnemonic's operand count
was genuinely never itemized in AUR-ARCH-005 (the "args"-style STREAM/SYSTEM
placeholders), the value is left as None (-> blank CSV cell / JSON null)
rather than invented.

Also fixes a data bug found while doing this: RET's operands list was
copy-pasted from CALL/JMP/JMPR as ["target/reg"], but RET takes no operand
(PC = R13, implicit).
"""
import csv
import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(_DIR, "aurora_v1_2_isa.json")
YAML_PATH = os.path.join(_DIR, "aurora_v1_2_isa.yaml")
CSV_PATH = os.path.join(_DIR, "aurora_v1_2_instruction_table.csv")
DOCS_CSV_PATH = os.path.join(os.path.dirname(_DIR), "..", "docs", "isa", "aurora_v1_2_instruction_table.csv")

# mnemonic -> (operand_count, immediate_bits); None means "not itemized in any source"
OPERAND_INFO = {
    # RRR (0x0) - 2-address written as 3 operands, no immediate
    "ADD": (3, 0), "SUB": (3, 0), "AND": (3, 0), "OR": (3, 0),
    "XOR": (3, 0), "CMP": (3, 0), "MIN": (3, 0), "MAX": (3, 0),
    # RRI (0x1) - Rd/Ra + 4-bit immediate (EXT-extendable)
    "ADDI": (2, 4), "SUBI": (2, 4), "ANDI": (2, 4), "ORI": (2, 4),
    "XORI": (2, 4), "CMPI": (2, 4),
    # SHIFT (0x2) - Rd/Ra + 4-bit count (dual-purpose: immediate OR Rs)
    "LSL": (2, 4), "LSR": (2, 4), "ASR": (2, 4), "ROL": (2, 4), "ROR": (2, 4),
    # RRR_OR_ACC (0x3) - same physical layout as RRR
    "MUL": (3, 0), "MULH": (3, 0), "MAC": (3, 0), "MAS": (3, 0),
    "DIVSTEP": (3, 0), "DIV": (3, 0),
    # DSP_RED (0x4) - acc select, src, fold flag, consume/local flag
    "REDUCE.ADD": (4, 0), "REDUCE.AND": (4, 0), "REDUCE.OR": (4, 0),
    "REDUCE.XOR": (4, 0), "REDUCE.MIN": (4, 0), "REDUCE.MAX": (4, 0),
    "REDUCE.ABSMAX": (4, 0), "REDUCE.COUNT": (4, 0),
    # DSP_DOT / DSP_SAD (0x4) - two sources, src1 needs a mandatory EXT word
    "DOT": (5, 0), "SAD": (5, 0),
    # RR_OR_UNARY (0x5) - real arity differs per mnemonic despite the shared
    # placeholder operand string in the CSV/JSON; PACK/UNPACK/ZIP/UNZIP follow
    # the same 2-address (Ra=Rd) convention as RRR, the rest are genuinely
    # 2-operand (or 2-operand+immediate for SHUFFLE's lane select).
    "PACK": (3, 0), "UNPACK": (3, 0), "ZIP": (3, 0), "UNZIP": (3, 0),
    "BSWAP": (2, 0), "WSWAP": (2, 0), "SHUFFLE": (3, 4), "MOV": (2, 0),
    "ZEXT8": (2, 0), "SEXT8": (2, 0), "ZEXT16": (2, 0), "SEXT16": (2, 0),
    # MEM (0x6/0x7) - Rd/Rs + [base] ; offset is 0 unless an EXT word attaches
    "LD": (2, 0), "ST": (2, 0),
    # BR (0x8) - single PC-relative target
    "B.EQ": (1, 8), "B.NE": (1, 8), "B.LT": (1, 8), "B.GE": (1, 8),
    "B.LTU": (1, 8), "B.GEU": (1, 8), "B.MI": (1, 8), "B.PL": (1, 8),
    # CTRL (0x9)
    "CALL": (1, 8), "JMP": (1, 8), "RET": (0, 0), "JMPR": (1, 0),
    # STACK (0xA) - single register or mask token; PUSHM/POPM mask needs EXT
    "PUSH": (1, 0), "POP": (1, 0), "PUSHM": (1, 0), "POPM": (1, 0),
    # STREAM (0xB) - QPEEK/QPUSH/QCFG confirmed by docx; rest inferred by
    # analogy (never individually itemized in any source found so far)
    "QMASK": (2, 6), "QPEEK": (2, 6), "QPUSH": (2, 6), "QPOP": (2, 6),
    "QDUP": (2, 6), "QREPL": (2, 6), "QCFG": (3, 6), "QCIRC": (2, 6),
    "QSTEP": (1, 0),
    # LOOP_AGU (0xC) - no ratified bit layout at all (see encoding.json conflict note)
    "LOOPSET": (None, None), "LOOPEND": (None, None),
    "AGUCFG": (None, None), "STRIDE": (None, None),
    # SYSTEM (0xD) - none of these were individually itemized; inferred
    "MRS": (2, 6), "MSR": (2, 6), "EI": (0, 0), "DI": (0, 0), "IRET": (0, 0),
    "ASCALL": (1, 6), "TIMERLOAD": (1, 6), "TIMERVEC": (1, 6),
    "TIMERCTL": (1, 6), "RDCYCLE": (1, 0),
    "MODE": (1, 3), "WFI": (0, 0), "WFE": (0, 0), "HALT": (0, 0),
    "CTXSAVE": (2, 8), "CTXRESTORE": (2, 8),
    # EXT / CUSTOM (0xE/0xF)
    "EXT": (1, 12), "CUSTOM": (1, 12),
}


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    missing = [i["mnemonic"] for i in data["instructions"] if i["mnemonic"] not in OPERAND_INFO]
    if missing:
        raise SystemExit(f"OPERAND_INFO missing entries for: {missing}")

    new_instructions = []
    for instr in data["instructions"]:
        if instr["mnemonic"] == "RET":
            instr["operands"] = []
        oc, ib = OPERAND_INFO[instr["mnemonic"]]
        new_instr = {}
        for k, v in instr.items():
            new_instr[k] = v
            if k == "operands":
                new_instr["operand_count"] = oc
                new_instr["immediate_bits"] = ib
        new_instructions.append(new_instr)
    data["instructions"] = new_instructions

    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    write_yaml(data)
    write_csv(CSV_PATH, data)
    write_csv(DOCS_CSV_PATH, data)
    print(f"Updated {len(new_instructions)} instructions.")


def yaml_scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        if v == "" or any(ch in v for ch in ":#{}[]&*!|>'\"%@`,") or v.strip() != v:
            return json.dumps(v)
        return v
    return str(v)


def write_yaml(data):
    lines = []
    lines.append(f'schema_version: {data["schema_version"]}')
    lines.append(f'architecture: {data["architecture"]}')
    # Preserve the rest of the header/registers/modes/etc. section verbatim
    # by reading it from the existing file (only the instructions: section
    # is regenerated) - the file is opened fresh below instead.
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        existing = f.read()
    header, _, _ = existing.partition("\ninstructions:\n")
    out = [header, "\ninstructions:\n"]
    for instr in data["instructions"]:
        out.append("  -\n")
        for k, v in instr.items():
            if isinstance(v, list):
                if not v:
                    out.append(f"    {k}:\n")
                else:
                    out.append(f"    {k}:\n")
                    for item in v:
                        out.append(f"      - {yaml_scalar(item)}\n")
            elif v is None:
                out.append(f"    {k}:\n")
            else:
                out.append(f"    {k}: {yaml_scalar(v)}\n")
    with open(YAML_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(out))


CSV_COLUMNS = [
    "mnemonic", "primary", "subop", "format", "operands", "operand_count",
    "immediate_bits", "semantics", "modes", "issue_slot", "latency",
    "initiation_interval", "flags", "exceptions", "attributes", "aliases",
]


def write_csv(path, data):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_COLUMNS)
        for instr in data["instructions"]:
            row = []
            for col in CSV_COLUMNS:
                v = instr.get(col, "")
                if isinstance(v, list):
                    v = "|".join(str(x) for x in v)
                elif v is None:
                    v = ""
                row.append(v)
            w.writerow(row)


if __name__ == "__main__":
    main()
