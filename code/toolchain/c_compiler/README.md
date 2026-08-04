# Aurora C Compiler

`aurora_cc.py` is a single-file C-to-Aurora-assembly compiler written in Python 3.
It translates a useful subset of C directly into Aurora v1.2 assembly mnemonics
that can be fed to an assembler targeting the Aurora chip.

## Usage

```
python3 aurora_cc.py <input.c> [-o <output.s>]
```

If `-o` is omitted the assembly is written to standard output.

```bash
# compile and view assembly
python3 aurora_cc.py examples/factorial.c

# compile to a file
python3 aurora_cc.py examples/sum_range.c -o sum_range.s
```

## Supported C subset

| Feature | Detail |
|---------|--------|
| **Types** | `int` (32-bit signed), `void` |
| **Globals** | `int x;` and `int x = <literal>;` at file scope |
| **Functions** | `int`/`void` return type, up to 4 `int` parameters |
| **Local variables** | `int x;` and `int x = <expr>;` anywhere in a block |
| **Arithmetic** | `+ - * / %` |
| **Bitwise** | `& \| ^ ~ << >>` |
| **Logical** | `&& \|\| !` (with short-circuit evaluation) |
| **Comparison** | `== != < <= > >=` |
| **Assignment** | `=` and compound `+= -= *= /= %= &= \|= ^= <<= >>=` |
| **Increment/decrement** | Pre and post `++` / `--` |
| **Control flow** | `if`/`else`, `while`, `for`, `return` |
| **Function calls** | Up to 4 integer arguments, integer return value |

## Calling convention (Aurora ABI)

| Register | Role |
|----------|------|
| R0–R3 | First four integer arguments; return value in R0 |
| R4–R12 | General-purpose temporaries (caller-saved: R4–R7, callee-saved: R8–R12) |
| R13 | Link register — holds return address after `CALL` |
| R14 | Stack pointer (SP); grows downward |
| R15 | Program counter — not accessible as a GPR in generated code |

## Stack frame layout

```
Higher addresses (before call)
┌──────────────────────────────┐
│  ...caller's frame...        │
├──────────────────────────────┤  ← SP on entry
│  saved LR (R13)   [4 bytes]  │
├──────────────────────────────┤  ← SP after PUSH R13
│  local 0 (param 0 / first    │
│           declared local)    │
│  local 1                     │
│  ...                         │
├──────────────────────────────┤  ← SP after prologue ADDI (frame_size subtracted)
Lower addresses
```

All locals are pre-allocated in a single prologue adjustment.
SP-relative offsets are fixed for the entire function lifetime.

## Assembly output notes

* Instructions follow the Aurora v1.2 ISA mnemonics defined in
  `isa/database/aurora_v1_2_instruction_table.csv`.
* Wide immediates that do not fit in the 4-bit immediate field are encoded
  using the `EXT` prefix instruction followed by the main instruction.
* Global variables are placed in a `.data` section with `.word` directives.
* Functions are placed in a `.text` section and exported with `.global`.
* Labels use the `.Ln` / `.<func>_end<n>` naming convention.

## Limitations / future work

* No pointer types, arrays, structs, or unions.
* No `char`/`short`/`long`/`float`/`double`.
* No `#include`, `#define`, or preprocessor directives.
* No variadic functions.
* No more than 4 arguments per function call.
* Register spilling is not implemented; very register-heavy expressions
  (more than 9 simultaneous live temporaries) will raise an error.
* No optimisation passes — output is straightforward but unoptimised.

## Examples

| File | Description |
|------|-------------|
| `examples/factorial.c` | Recursive factorial |
| `examples/sum_range.c` | Iterative sum with a `for` loop and a global variable |
| `examples/bitops.c` | Bit manipulation: population count and count-leading-zeros |
