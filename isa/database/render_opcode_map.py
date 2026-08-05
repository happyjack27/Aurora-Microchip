"""
One-off, dependency-free PNG renderer for the Aurora v1.2 opcode-space map.
No matplotlib/Pillow available in this environment, so this writes raw PNG
bytes (IHDR/IDAT/IEND) directly via zlib + struct - no external packages.

Draws a 16 (primary) x 16 (subop) grid. Each row = one primary opcode family.
Within a row: solid family color = assigned subop, pale tint = free/remaining.
Special-cased rows (0x6/0x7/0xE/0xF) are drawn fully solid with a hatch
overlay because their subop byte is not an instruction-selecting field.
"""
import struct
import zlib

CELL = 40
COLS = 16
ROWS = 16
W = CELL * COLS
H = CELL * ROWS

# family -> (name, base color, set of used subops or 'ALL'/'ALL-HATCH', note)
FAMILIES = {
    0x0: ("ALU_REG",     (66, 133, 244),  set(range(0, 8)),  None),
    0x1: ("ALU_IMM",     (52, 168, 235),  set(range(0, 6)),  None),
    0x2: ("SHIFT_ROT",   (26, 188, 211),  set(range(0, 5)),  None),
    0x3: ("MULDIV",      (0, 150, 136),   set(range(0, 6)),  None),
    0x4: ("DSP_REDUCE",  (76, 175, 80),   set(range(0, 10)), None),
    0x5: ("REG_LAYOUT",  (139, 195, 74),  set(range(0, 12)), None),
    0x6: ("LOAD",        (255, 193, 7),   "ALL-HATCH", "mode/width uses subop byte"),
    0x7: ("STORE",       (255, 152, 0),   "ALL-HATCH", "mode/width uses subop byte"),
    0x8: ("BRANCH",      (233, 30, 99),   set(range(0, 8)),  None),
    0x9: ("CTRL_FLOW",   (156, 39, 176),  set(range(0, 4)),  None),
    0xA: ("STACK",       (103, 58, 183),  set(range(0, 4)),  None),
    0xB: ("STREAM",      (63, 81, 181),   set(range(0, 10)), None),
    0xC: ("LOOP",        (121, 85, 72),   set(range(0, 3)),  "0=LOOP 1=NOP 2=LOOPR (ADR-ISA-020/022); AGUCFG/STRIDE retired, 3-9 reserved"),
    0xD: ("SYSTEM",      (244, 67, 54),   set(range(0, 16)), "FULLY PACKED - 0 free"),
    0xE: ("EXT",         (158, 158, 158), "ALL-HATCH", "prefix escape, not subop-indexed"),
    0xF: ("CUSTOM",      (117, 117, 117), "ALL-HATCH", "reserved implementation-defined"),
}

FREE_TINT = 0.88  # how close to white the "free" cells are (0=full color,1=white)


def blend_white(c, t):
    return tuple(int(v + (255 - v) * t) for v in c)


def make_pixels():
    px = [[(255, 255, 255) for _ in range(W)] for _ in range(H)]
    for primary in range(16):
        name, color, used, note = FAMILIES[primary]
        for subop in range(16):
            if used == "ALL-HATCH":
                # solid family color with a diagonal hatch stripe every 8px
                is_used = True
            else:
                is_used = subop in used
            cell_color = color if is_used else blend_white(color, FREE_TINT)
            y0, x0 = primary * CELL, subop * CELL
            for yy in range(CELL):
                for xx in range(CELL):
                    c = cell_color
                    if used == "ALL-HATCH" and (xx + yy) % 10 < 2:
                        c = blend_white(color, 0.35)
                    # grid lines
                    if xx == 0 or yy == 0:
                        c = (30, 30, 30)
                    px[y0 + yy][x0 + xx] = c
    return px


def write_png(path, px):
    height = len(px)
    width = len(px[0])
    raw = bytearray()
    for row in px:
        raw.append(0)  # filter type 0 (none)
        for (r, g, b) in row:
            raw += bytes((r, g, b))
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(sig)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", compressed))
        f.write(chunk(b"IEND", b""))


if __name__ == "__main__":
    write_png(r"C:\Users\kbaas\git\Aurora-Microchip\docs\isa\aurora_v1_2_opcode_space_map.png", make_pixels())
    print("wrote map")
