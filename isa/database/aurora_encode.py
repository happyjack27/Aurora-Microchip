"""
Aurora v1.2 mnemonic <-> 16-bit machine-word encoder/decoder.

Combines:
  - aurora_v1_2_isa.json      (mnemonic -> primary/subop/format/operands)
  - aurora_v1_2_encoding.json (format -> bit-field layout)

into a working translation from a mnemonic + operand values to the literal
16-bit instruction word (and back).

Run this file directly to execute self-tests against the two worked hex
examples published in AUR-ARCH-005 ("Reading a Complete Bytecode"):
    ADD R1, R1, R2      -> 0x0012
    DIVSTEP R1, R1, R2  -> 0x3412

Usage:
    from aurora_encode import Aurora
    a = Aurora()
    a.encode("ADD", rd=1, rb=2)          -> 0x0012
    a.encode("ADDI", rd=3, imm=5)        -> ...
    a.encode("MODE", mode="PACKED16")    -> ...
    a.decode(0x0012)                     -> {"mnemonic": "ADD", "primary": 0, "subop": 0, "fields": {...}}

NOTE: Formats marked "inferred" in aurora_v1_2_encoding.json are NOT yet
ratified by AUR-ARCH-005 - they are provisional layouts designed here only to
unblock mnemonic->bit translation. See that file's per-format "status"/
"source" keys before treating any particular field position as final.
"""
from __future__ import annotations

import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
ISA_JSON = os.path.join(_DIR, "aurora_v1_2_isa.json")
ENCODING_JSON = os.path.join(_DIR, "aurora_v1_2_encoding.json")


def _bitmask(hi: int, lo: int) -> int:
    width = hi - lo + 1
    return ((1 << width) - 1) << lo


def pack_field(word: int, bits: list[int], value: int) -> int:
    """Return `word` with `value` written into inclusive bit range bits=[hi, lo]."""
    hi, lo = bits
    width = hi - lo + 1
    mask = (1 << width) - 1
    if value < -(1 << (width - 1)) or value > (1 << width) - 1:
        raise ValueError(f"value {value} does not fit in {width} bits")
    word &= ~_bitmask(hi, lo)
    word |= (value & mask) << lo
    return word & 0xFFFF


def extract_field(word: int, bits: list[int], signed: bool = False) -> int:
    hi, lo = bits
    width = hi - lo + 1
    mask = (1 << width) - 1
    value = (word >> lo) & mask
    if signed and value & (1 << (width - 1)):
        value -= (1 << width)
    return value


class AuroraEncodingError(Exception):
    pass


class Aurora:
    def __init__(self, isa_path: str = ISA_JSON, encoding_path: str = ENCODING_JSON):
        with open(isa_path, "r", encoding="utf-8") as f:
            self.isa = json.load(f)
        with open(encoding_path, "r", encoding="utf-8") as f:
            self.encoding = json.load(f)
        self.by_mnemonic = {i["mnemonic"]: i for i in self.isa["instructions"]}
        self.formats = self.encoding["formats"]

    # ------------------------------------------------------------------
    # Core packing helpers
    # ------------------------------------------------------------------
    def _base(self, instr: dict) -> int:
        primary = int(instr["primary"], 16)
        word = pack_field(0, [15, 12], primary)
        fmt = self.formats.get(instr["format"])
        if fmt and any(f["name"] == "subop" for f in fmt["fields"]):
            subop_field = next(f for f in fmt["fields"] if f["name"] == "subop")
            word = pack_field(word, subop_field["bits"], instr["subop"])
        return word

    def _format_of(self, mnemonic: str) -> tuple[dict, dict]:
        instr = self.by_mnemonic.get(mnemonic)
        if instr is None:
            raise AuroraEncodingError(f"unknown mnemonic {mnemonic!r}")
        fmt = self.formats.get(instr["format"])
        if fmt is None:
            raise AuroraEncodingError(
                f"no encoding table entry for format {instr['format']!r} (mnemonic {mnemonic!r})"
            )
        return instr, fmt

    # ------------------------------------------------------------------
    # Per-format encoders
    # ------------------------------------------------------------------
    def encode(self, mnemonic: str, **kw) -> int:
        instr, fmt = self._format_of(mnemonic)
        fmt_name = instr["format"]
        handler = getattr(self, f"_encode_{fmt_name}", None)
        if handler is None:
            raise NotImplementedError(
                f"no encoder implemented yet for format {fmt_name!r} "
                f"(status={fmt.get('status')}); see aurora_v1_2_encoding.json"
            )
        return handler(instr, fmt, **kw)

    def _field_bits(self, fmt: dict, name: str) -> list[int]:
        for f in fmt["fields"]:
            if f["name"] == name:
                return f["bits"]
        raise AuroraEncodingError(f"format has no field {name!r}")

    def _encode_RRR(self, instr, fmt, rd: int, rb: int, ra: int | None = None) -> int:
        # 2-address compact form: Rd and Ra share one physical field and must agree.
        if ra is not None and ra != rd:
            raise AuroraEncodingError("RRR format is 2-address: Ra must equal Rd")
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "Rd_Ra"), rd)
        word = pack_field(word, self._field_bits(fmt, "Rb"), rb)
        return word

    _encode_RRR_OR_ACC = _encode_RRR

    def _encode_RRR_ACC(self, instr, fmt, ra: int, rb: int, accumulator: str | int = "A0") -> int:
        # MAC/MAS: Ra/Rb are independent operands (no 2-address constraint); accumulator
        # selection lives in the bit freed by RRR_OR_ACC's subop needing only 3 bits.
        if isinstance(accumulator, str):
            inv = {v: int(k) for k, v in fmt["acc_enum"].items()}
            if accumulator not in inv:
                raise AuroraEncodingError(f"unknown accumulator {accumulator!r}")
            accumulator = inv[accumulator]
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "acc_sel"), accumulator)
        word = pack_field(word, self._field_bits(fmt, "Ra"), ra)
        word = pack_field(word, self._field_bits(fmt, "Rb"), rb)
        return word

    def _encode_RRI(self, instr, fmt, rd: int, imm4: int, ra: int | None = None) -> int:
        if ra is not None and ra != rd:
            raise AuroraEncodingError("RRI format is 2-address: Ra must equal Rd")
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "Rd_Ra"), rd)
        word = pack_field(word, self._field_bits(fmt, "IMM4"), imm4)
        return word

    def _encode_SHIFT(self, instr, fmt, rd: int, count_or_rs: int, ra: int | None = None) -> int:
        if ra is not None and ra != rd:
            raise AuroraEncodingError("SHIFT format is 2-address: Ra must equal Rd")
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "Rd_Ra"), rd)
        word = pack_field(word, self._field_bits(fmt, "count_or_Rs"), count_or_rs)
        return word

    def _encode_MEM(self, instr, fmt, rd_rs: int, base_or_off: int, mode_width: int = 0) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "mode_width"), mode_width)
        word = pack_field(word, self._field_bits(fmt, "Rd_Rs"), rd_rs)
        word = pack_field(word, self._field_bits(fmt, "base_or_off"), base_or_off)
        return word

    def _encode_BR(self, instr, fmt, disp8: int) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "disp8"), disp8)
        return word

    def _encode_RR_OR_UNARY(self, instr, fmt, rd: int, rs: int = 0) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "Rd"), rd)
        word = pack_field(word, self._field_bits(fmt, "Rs_or_Rb"), rs)
        return word

    def _encode_MODE_IMM(self, instr, fmt, mode) -> int:
        mode_enum = fmt["mode_enum"]
        if isinstance(mode, str):
            inv = {v: int(k) for k, v in mode_enum.items()}
            if mode not in inv:
                raise AuroraEncodingError(f"unknown mode {mode!r}")
            mode = inv[mode]
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "mode"), mode)
        return word

    def _encode_SYSTEM_NONE(self, instr, fmt) -> int:
        return self._base(instr)

    def _encode_STREAM_QSTEP(self, instr, fmt, qn: int) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "Qn"), qn)
        return word

    def _encode_STREAM(self, instr, fmt, select: int = 0, control_arg: int = 0) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "select"), select)
        word = pack_field(word, self._field_bits(fmt, "control_arg"), control_arg)
        return word

    _encode_SYSTEM = _encode_STREAM

    def _encode_STACK(self, instr, fmt, reg_or_flag: int = 0) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "reg_or_flag"), reg_or_flag)
        return word

    def _encode_CTRL(self, instr, fmt, reg_or_disp: int = 0) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "reg_or_disp"), reg_or_disp)
        return word

    def _encode_SYSTEM_CTX(self, instr, fmt, mask: int, rbase: int) -> tuple[int, int]:
        """Returns (base_word, ext_word) - this format mandatorily needs an EXT word for Rbase."""
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "mask"), mask)
        ext_fmt = self.formats["EXT"]
        ext_word = pack_field(0, self._field_bits(ext_fmt, "primary"), 0xE)
        ext_word = pack_field(ext_word, [3, 0], rbase)
        return word, ext_word

    def _encode_LOOP_IMM8(self, instr, fmt, count: int | None = None) -> int:
        word = self._base(instr)
        if instr["mnemonic"] == "LOOP":
            if count is None or not (1 <= count <= 256):
                raise AuroraEncodingError("LOOP requires count=1..256")
            word = pack_field(word, self._field_bits(fmt, "count_minus_one"), count - 1)
        return word

    def _encode_LOOP_REG(self, instr, fmt, rs: int) -> int:
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "Rs"), rs)
        return word

    def _encode_STREAM_POPMETA(self, instr, fmt, rd: int, qn: int = 0) -> int:
        if rd % 2 != 0:
            raise AuroraEncodingError("POPMETA requires an even-aligned Rd:Rd+1 register pair")
        word = self._base(instr)
        word = pack_field(word, self._field_bits(fmt, "Rd"), rd)
        word = pack_field(word, self._field_bits(fmt, "Qn"), qn)
        return word

    # ------------------------------------------------------------------
    # Decode
    # ------------------------------------------------------------------
    def decode(self, word: int) -> dict:
        primary = extract_field(word, [15, 12])
        candidates = [i for i in self.isa["instructions"] if int(i["primary"], 16) == primary]
        if not candidates:
            return {"primary": primary, "mnemonic": None, "fields": {}}
        # narrow by subop where the format has one
        best = None
        for instr in candidates:
            fmt = self.formats.get(instr["format"])
            if fmt is None:
                continue
            subop_field = next((f for f in fmt["fields"] if f["name"] == "subop"), None)
            if subop_field is None:
                best = instr
                break
            if extract_field(word, subop_field["bits"]) == instr["subop"]:
                best = instr
                break
        if best is None:
            return {"primary": primary, "mnemonic": None, "fields": {}}
        fmt = self.formats[best["format"]]
        fields = {}
        for f in fmt["fields"]:
            fields[f["name"]] = extract_field(word, f["bits"], signed=f.get("signed", False))
        return {"mnemonic": best["mnemonic"], "primary": primary, "format": best["format"], "fields": fields}


def _self_test() -> None:
    a = Aurora()

    # AUR-ARCH-005 Sec.5 worked example: ADD R1, R1, R2 -> 0x0012
    w = a.encode("ADD", rd=1, rb=2)
    assert w == 0x0012, f"ADD R1,R1,R2 expected 0x0012, got {w:#06x}"

    # AUR-ARCH-005 Sec.5 worked example: DIVSTEP R1, R1, R2 -> 0x3412
    w = a.encode("DIVSTEP", rd=1, rb=2)
    assert w == 0x3412, f"DIVSTEP R1,R1,R2 expected 0x3412, got {w:#06x}"

    d = a.decode(0x0012)
    assert d["mnemonic"] == "ADD", d

    d = a.decode(0x3412)
    assert d["mnemonic"] == "DIVSTEP", d

    # MAC A0, R2, R3 -> primary 0x3, acc_sel=0, subop=2, Ra=2, Rb=3 -> 0011 0010 0010 0011 = 0x3223
    w = a.encode("MAC", ra=2, rb=3, accumulator="A0")
    assert w == 0x3223, f"MAC A0,R2,R3 expected 0x3223, got {w:#06x}"

    # MAC A1, R2, R3 -> acc_sel=1 -> 0011 1010 0010 0011 = 0x3A23
    w = a.encode("MAC", ra=2, rb=3, accumulator="A1")
    assert w == 0x3A23, f"MAC A1,R2,R3 expected 0x3A23, got {w:#06x}"

    # MAS A1, R2, R3 -> subop=3, acc_sel=1 -> 0011 1011 0010 0011 = 0x3B23
    w = a.encode("MAS", ra=2, rb=3, accumulator="A1")
    assert w == 0x3B23, f"MAS A1,R2,R3 expected 0x3B23, got {w:#06x}"

    d = a.decode(0x3A23)
    assert d["mnemonic"] == "MAC" and d["fields"]["acc_sel"] == 1, d

    # MODE #PACKED16 -> primary 0xD, subop 0xA(10), mode=1 -> 1101 1010 0010 0000 = 0xDA20
    w = a.encode("MODE", mode="PACKED16")
    assert w == 0xDA20, f"MODE #PACKED16 expected 0xDA20, got {w:#06x}"

    # WFI -> primary 0xD, subop 0xB(11), rest 0 -> 1101 1011 0000 0000 = 0xDB00
    w = a.encode("WFI")
    assert w == 0xDB00, f"WFI expected 0xDB00, got {w:#06x}"

    # QSTEP Q1 -> primary 0xB, subop 0x8, Qn=1 -> 1011 1000 0001 0000 = 0xB810
    w = a.encode("QSTEP", qn=1)
    assert w == 0xB810, f"QSTEP Q1 expected 0xB810, got {w:#06x}"

    # POPMETA R4:R5, Q0 -> primary 0xB, subop 9, Rd=4, Qn=0 -> 1011 1001 0100 0000 = 0xB940
    w = a.encode("POPMETA", rd=4, qn=0)
    assert w == 0xB940, f"POPMETA R4:R5,Q0 expected 0xB940, got {w:#06x}"

    # LOOP #16 -> primary 0xC, subop 0, count_minus_one=15 -> 1100 0000 0000 1111 = 0xC00F
    w = a.encode("LOOP", count=16)
    assert w == 0xC00F, f"LOOP #16 expected 0xC00F, got {w:#06x}"

    # NOP -> primary 0xC, subop 1, rest 0 -> 1100 0001 0000 0000 = 0xC100
    w = a.encode("NOP")
    assert w == 0xC100, f"NOP expected 0xC100, got {w:#06x}"

    # LOOPR R3 -> primary 0xC, subop 2, Rs=3, reserved 0 -> 1100 0010 0011 0000 = 0xC230
    w = a.encode("LOOPR", rs=3)
    assert w == 0xC230, f"LOOPR R3 expected 0xC230, got {w:#06x}"

    # POPMETA requires an even-aligned Rd:Rd+1 pair - odd Rd must be rejected
    try:
        a.encode("POPMETA", rd=5, qn=0)
        raise AssertionError("POPMETA with odd Rd=5 should have raised AuroraEncodingError")
    except AuroraEncodingError:
        pass

    # Retired mnemonics (LOOPSET/LOOPEND/AGUCFG/STRIDE) must not be assemblable
    for retired in ("LOOPSET", "LOOPEND", "AGUCFG", "STRIDE"):
        try:
            a.encode(retired)
            raise AssertionError(f"retired mnemonic {retired!r} should not encode")
        except AuroraEncodingError:
            pass

    print("All self-tests passed.")


if __name__ == "__main__":
    _self_test()
