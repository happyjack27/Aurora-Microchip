/*
 * aurora_asm.c — Two-pass assembler for the Aurora v1.2 architecture
 *
 * Instruction word: 16-bit, little-endian
 * Registers:        R0–R15 (R14 = SP, R15 = PC)
 * Immediates:       decimal, 0x hex, 0b binary, 0o octal
 * Labels:           identifier followed by ':'
 * Directives:       .org, .word, .byte, .equ / .set
 * Comments:         ; to end of line  or  // to end of line
 *
 * Output formats (selectable with -f):
 *   bin  — raw little-endian 16-bit words (default)
 *   hex  — Intel HEX (IHEX)
 *   vhex — Verilog $readmemh one word per line
 *
 * Usage:
 *   aurora_asm [-o outfile] [-f bin|hex|vhex] infile.asm
 */

#define _POSIX_C_SOURCE 200809L
#include <ctype.h>
#include <errno.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

/* ───────────────────────── limits ───────────────────────── */
#define MAX_SYMBOLS   4096
#define MAX_LINES     65536
#define MAX_WORDS     65536   /* 128 KiB / 2 bytes each */
#define MAX_TOK       32
#define MAX_LABEL_LEN 128
#define MAX_LINE_LEN  512

/* ───────────────────────── helpers ──────────────────────── */
static void die(const char *fmt, ...) {
    va_list ap; va_start(ap, fmt);
    fprintf(stderr, "aurora_asm: error: ");
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
    exit(1);
}

static int lineno = 0; /* current line for error messages */
static void err(const char *fmt, ...) {
    va_list ap; va_start(ap, fmt);
    fprintf(stderr, "aurora_asm: line %d: ", lineno);
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
    exit(1);
}

static void warn(const char *fmt, ...) {
    va_list ap; va_start(ap, fmt);
    fprintf(stderr, "aurora_asm: warning: line %d: ", lineno);
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
}

/* ────────────────────── symbol table ────────────────────── */
typedef struct { char name[MAX_LABEL_LEN]; int32_t value; } Symbol;
static Symbol symbols[MAX_SYMBOLS];
static int nsym = 0;

static Symbol *sym_find(const char *name) {
    for (int i = 0; i < nsym; i++)
        if (!strcmp(symbols[i].name, name))
            return &symbols[i];
    return NULL;
}

static void sym_define(const char *name, int32_t value) {
    Symbol *s = sym_find(name);
    if (s) { s->value = value; return; }
    if (nsym >= MAX_SYMBOLS) die("symbol table overflow");
    snprintf(symbols[nsym].name, MAX_LABEL_LEN, "%s", name);
    symbols[nsym].value = value;
    nsym++;
}

/* resolve symbol; returns 1 on success, 0 if undefined */
static int sym_resolve(const char *name, int32_t *out) {
    Symbol *s = sym_find(name);
    if (!s) return 0;
    *out = s->value;
    return 1;
}

/* ─────────────────────── output buffer ──────────────────── */
static uint16_t words[MAX_WORDS];
static int      nwords = 0;  /* total words written so far */
static uint32_t org = 0;     /* current byte address (PC × 2) */

static int addr_to_idx(uint32_t byte_addr) {
    return (int)(byte_addr / 2);
}

static void emit(uint16_t w) {
    int idx = addr_to_idx(org);
    if (idx >= MAX_WORDS) err("output address 0x%x out of range", org);
    words[idx] = w;
    if (idx >= nwords) nwords = idx + 1;
    org += 2;
}

/* ───────────────────────── tokeniser ────────────────────── */

/* strip leading/trailing whitespace in-place */
static char *trim(char *s) {
    while (*s && isspace((unsigned char)*s)) s++;
    char *e = s + strlen(s);
    while (e > s && isspace((unsigned char)*(e-1))) e--;
    *e = '\0';
    return s;
}

/* split line into tokens (comma and whitespace delimited) */
static int tokenise(char *line, char *toks[], int maxtok) {
    int n = 0;
    char *p = line;
    while (*p) {
        while (*p && (isspace((unsigned char)*p) || *p == ',')) p++;
        if (!*p) break;
        if (n >= maxtok) err("too many tokens");
        toks[n++] = p;
        while (*p && *p != ',' && !isspace((unsigned char)*p)) p++;
        if (*p) *p++ = '\0';
    }
    return n;
}

/* strip comments (; or //) */
static void strip_comment(char *line) {
    char *p = line;
    int in_sq = 0; /* inside [] */
    while (*p) {
        if (*p == '[') in_sq = 1;
        if (*p == ']') in_sq = 0;
        if (!in_sq) {
            if (*p == ';') { *p = '\0'; return; }
            if (*p == '/' && *(p+1) == '/') { *p = '\0'; return; }
        }
        p++;
    }
}

/* ────────────────── expression / immediate parser ────────── */
/* Supports: decimal, 0xNN hex, 0bNN binary, 0oNN octal, symbols */
static int parse_imm(const char *tok, int32_t *out) {
    if (!tok || !*tok) return 0;
    char *end;
    /* hex */
    if (tok[0] == '0' && (tok[1] == 'x' || tok[1] == 'X')) {
        *out = (int32_t)strtoul(tok+2, &end, 16);
        return (*end == '\0');
    }
    /* binary */
    if (tok[0] == '0' && (tok[1] == 'b' || tok[1] == 'B')) {
        *out = (int32_t)strtoul(tok+2, &end, 2);
        return (*end == '\0');
    }
    /* octal */
    if (tok[0] == '0' && (tok[1] == 'o' || tok[1] == 'O')) {
        *out = (int32_t)strtoul(tok+2, &end, 8);
        return (*end == '\0');
    }
    /* decimal (may be negative) */
    if (isdigit((unsigned char)tok[0]) || tok[0] == '-') {
        *out = (int32_t)strtol(tok, &end, 10);
        return (*end == '\0');
    }
    /* symbol */
    return sym_resolve(tok, out);
}

/* parse immediate; error if unresolvable (pass 2 only) */
static int32_t need_imm(const char *tok) {
    int32_t v;
    if (!parse_imm(tok, &v))
        err("undefined symbol or bad immediate: '%s'", tok);
    return v;
}

/* ─────────────────────── register parser ─────────────────── */
/* Accepts R0..R15, SP (=R14), PC (=R15), LR (=R13) */
static int parse_reg(const char *tok) {
    if (!tok) return -1;
    if (!strncasecmp(tok, "SP", 2)  && strlen(tok) == 2) return 14;
    if (!strncasecmp(tok, "PC", 2)  && strlen(tok) == 2) return 15;
    if (!strncasecmp(tok, "LR", 2)  && strlen(tok) == 2) return 13;
    if ((tok[0] == 'R' || tok[0] == 'r') && isdigit((unsigned char)tok[1])) {
        int n = atoi(tok+1);
        if (n >= 0 && n <= 15) return n;
    }
    return -1;
}

static int need_reg(const char *tok) {
    int r = parse_reg(tok);
    if (r < 0) err("expected register, got '%s'", tok ? tok : "(null)");
    return r;
}

/* ─────────────────── memory operand parser ──────────────── */
/* Parses [base] or [base+offset] or [base+Roffset]
   Returns base reg, and sets *offset or *reg_off */
static void parse_mem(const char *tok, int *base, int *reg_off, int32_t *imm_off) {
    /* tok looks like "[Ra+5]" or "[Ra]" or "[Ra+Rb]" */
    char buf[MAX_LINE_LEN];
    snprintf(buf, sizeof(buf), "%s", tok);
    char *s = buf;
    if (*s != '[') err("expected '[' in memory operand, got '%s'", tok);
    s++;
    char *e = strchr(s, ']');
    if (!e) err("missing ']' in memory operand '%s'", tok);
    *e = '\0';
    /* find '+' or '-' separator */
    char *plus = strpbrk(s, "+-");
    *reg_off = -1; *imm_off = 0;
    if (plus) {
        int sign = (*plus == '-') ? -1 : 1;
        *plus = '\0';
        char *off_str = plus + 1;
        *base = need_reg(s);
        int r = parse_reg(off_str);
        if (r >= 0) {
            *reg_off = r;
        } else {
            int32_t v;
            if (!parse_imm(off_str, &v)) err("bad offset in '%s'", tok);
            *imm_off = sign * v;
        }
    } else {
        *base = need_reg(s);
    }
}

/* ─────────────────── instruction encoding ──────────────── */
/*
 * Encoding summary (16-bit word, big-field notation [15:0]):
 *
 * RRR / RRR_OR_ACC:
 *   [15:12] = primary  [11:8] = subop  [7:4] = Rd/Ra  [3:0] = Rb
 *
 * RRI (immediate):
 *   [15:12] = primary  [11:8] = subop  [7:4] = Rd/Ra  [3:0] = imm4
 *   (if imm > 4 bits: emit EXT word first carrying upper bits)
 *
 * SHIFT:
 *   [15:12] = primary  [11:8] = subop  [7:4] = Rd/Ra  [3:0] = count/Rs
 *
 * MEM (LD/ST):
 *   [15:12] = primary  [11:8] = mode_width  [7:4] = Rd/Rs  [3:0] = base/off
 *   (base reg in [3:0]; if offset != 0, EXT word follows with offset)
 *
 * BR:
 *   [15:12] = primary  [11:8] = cond  [7:0] = disp8 (signed, PC-relative word)
 *
 * CTRL (CALL/JMP/RET/JMPR):
 *   [15:12] = primary  [11:8] = subop  [7:0] = disp8 / [3:0] = Rs
 *
 * STACK (PUSH/POP/PUSHM/POPM):
 *   [15:12] = primary  [11:8] = subop  [7:4] = Rd/Rs  [3:0] = 0
 *
 * STREAM (Q* instructions):
 *   [15:12] = primary  [11:8] = subop  [7:6] = select  [5:0] = control_arg
 *
 * STREAM_QSTEP:
 *   [15:12] = primary  [11:8] = subop  [7:4] = Qn  [3:0] = 0
 *
 * LOOP_AGU (LOOPSET/LOOPEND/AGUCFG/STRIDE):
 *   [15:12] = primary  [11:8] = subop  [7:0] = args
 *
 * SYSTEM / MODE_IMM / SYSTEM_NONE / SYSTEM_CTX:
 *   [15:12] = primary  [11:8] = subop  [7:0] = control_arg / mode / mask
 *
 * DSP_RED (REDUCE.*):
 *   [15:12] = primary  [11:8] = subop
 *   [7]     = acc_sel   [6:3] = src   [2] = fold  [1] = local  [0] = 0
 *
 * DSP_DOT / DSP_SAD:
 *   [15:12] = primary  [11:8] = subop
 *   [7]     = acc_sel   [6:3] = src0  [2:0] = 0
 *   + mandatory EXT word [3:0] = src1
 *
 * RR_OR_UNARY (PACK/UNPACK/ZIP/UNZIP/BSWAP/WSWAP/SHUFFLE/MOV/ZEXT8/SEXT8/ZEXT16/SEXT16):
 *   [15:12] = primary  [11:8] = subop  [7:4] = Rd  [3:0] = Rs
 *
 * EXT word:
 *   [15:12] = 0xE  [11:0] = payload (12 bits)
 */

#define FIELD(val, hi, lo)   (((uint16_t)(val) & ((1u << ((hi)-(lo)+1))-1u)) << (lo))
#define EXT_PRIMARY          0xE

static uint16_t mk_rrr(int primary, int subop, int rd, int rb) {
    return FIELD(primary,15,12)|FIELD(subop,11,8)|FIELD(rd,7,4)|FIELD(rb,3,0);
}
static uint16_t mk_rri(int primary, int subop, int rd, int imm4) {
    return FIELD(primary,15,12)|FIELD(subop,11,8)|FIELD(rd,7,4)|FIELD(imm4,3,0);
}
static uint16_t mk_ext(int payload12) {
    return FIELD(EXT_PRIMARY,15,12)|FIELD(payload12,11,0);
}
static uint16_t mk_br(int cond, int disp8) {
    return FIELD(0x8,15,12)|FIELD(cond,11,8)|FIELD(disp8,7,0);
}
static uint16_t mk_ctrl(int subop, int disp8) {
    return FIELD(0x9,15,12)|FIELD(subop,11,8)|FIELD(disp8,7,0);
}
static uint16_t mk_stack(int subop, int reg) {
    return FIELD(0xA,15,12)|FIELD(subop,11,8)|FIELD(reg,7,4);
}
static uint16_t mk_stream(int subop, int select, int ctrl_arg) {
    return FIELD(0xB,15,12)|FIELD(subop,11,8)|FIELD(select,7,6)|FIELD(ctrl_arg,5,0);
}
static uint16_t mk_system(int subop, int ctrl_arg) {
    return FIELD(0xD,15,12)|FIELD(subop,11,8)|FIELD(ctrl_arg,7,0);
}
static uint16_t mk_dsp_red(int subop, int acc_sel, int src, int fold, int local_f) {
    return FIELD(0x4,15,12)|FIELD(subop,11,8)|FIELD(acc_sel,7,7)
          |FIELD(src,6,3)|FIELD(fold,2,2)|FIELD(local_f,1,1);
}
static uint16_t mk_loop(int subop, int args8) {
    return FIELD(0xC,15,12)|FIELD(subop,11,8)|FIELD(args8,7,0);
}

/* ─────────────────────── pass state ──────────────────────── */
typedef enum { PASS1, PASS2 } Pass;
static Pass pass;

/* on pass 1, skip instruction emission but advance PC */
#define EMIT(w)  do { if(pass==PASS2) emit(w); else org+=2; } while(0)

/* ─────────────────────── assemble one line ───────────────── */
static void assemble_line(char *line) {
    strip_comment(line);
    line = trim(line);
    if (!*line) return;

    /* label detection */
    char *colon = strchr(line, ':');
    if (colon) {
        /* make sure it is a proper label (no whitespace before ':') */
        char *space = strchr(line, ' ');
        if (!space || colon < space) {
            char lbl[MAX_LABEL_LEN];
            int len = (int)(colon - line);
            if (len <= 0 || len >= MAX_LABEL_LEN) err("bad label");
            strncpy(lbl, line, (size_t)len);
            lbl[len] = '\0';
            sym_define(lbl, (int32_t)org);
            line = trim(colon + 1);
            if (!*line) return;
        }
    }

    /* split into mnemonic + operands */
    char buf[MAX_LINE_LEN];
    snprintf(buf, sizeof(buf), "%s", line);
    char *toks[MAX_TOK];
    int ntok = tokenise(buf, toks, MAX_TOK);
    if (ntok == 0) return;

    const char *mn = toks[0];

    /* ── directives ── */
    if (!strcasecmp(mn, ".org")) {
        if (ntok < 2) err(".org requires address");
        int32_t addr = need_imm(toks[1]);
        org = (uint32_t)addr;
        return;
    }
    if (!strcasecmp(mn, ".word")) {
        for (int i = 1; i < ntok; i++) {
            int32_t v = need_imm(toks[i]);
            EMIT((uint16_t)(v & 0xFFFF));
        }
        return;
    }
    if (!strcasecmp(mn, ".byte")) {
        /* pack pairs of bytes into words, little-endian */
        for (int i = 1; i < ntok; i += 2) {
            int32_t lo = need_imm(toks[i]);
            int32_t hi = (i+1 < ntok) ? need_imm(toks[i+1]) : 0;
            EMIT((uint16_t)((hi & 0xFF) << 8 | (lo & 0xFF)));
        }
        return;
    }
    if (!strcasecmp(mn, ".equ") || !strcasecmp(mn, ".set")) {
        if (ntok < 3) err("%s requires name, value", mn);
        int32_t v = need_imm(toks[2]);
        sym_define(toks[1], v);
        return;
    }

    /* ── instructions ── */

    /* --- ALU_REG (primary 0x0) --- */
#define ALU_REG_OP(MNEM, SUBOP) \
    if (!strcasecmp(mn, MNEM)) { \
        if (ntok < 4) err(MNEM " Rd, Ra, Rb"); \
        int rd = need_reg(toks[1]), ra = need_reg(toks[2]), rb = need_reg(toks[3]); \
        EMIT(mk_rrr(0x0, SUBOP, rd, ra)); \
        (void)rb; \
        /* Note: RRR packs Rd and Ra in [7:4] as Rd_Ra (dest==src0 compacted), Rb in [3:0] */ \
        /* Actual layout: [7:4]=Rd, but spec says "Rd_Ra" field -- treat as Rd */ \
        EMIT_CORRECTED: ; \
        if (pass == PASS2) { words[addr_to_idx(org-2)] = mk_rrr(0x0, SUBOP, rd, rb); (void)ra; } \
        return; \
    }
    /* Inline the ALU_REG instructions directly to avoid macro complexity: */

    /* ADD SUB AND OR XOR CMP MIN MAX */
    if (!strcasecmp(mn, "ADD") || !strcasecmp(mn, "SUB") ||
        !strcasecmp(mn, "AND") || !strcasecmp(mn, "OR")  ||
        !strcasecmp(mn, "XOR") || !strcasecmp(mn, "CMP") ||
        !strcasecmp(mn, "MIN") || !strcasecmp(mn, "MAX")) {
        if (ntok < 4) err("%s Rd, Ra, Rb", mn);
        static const char *names[] = {"ADD","SUB","AND","OR","XOR","CMP","MIN","MAX"};
        int subop = -1;
        for (int i = 0; i < 8; i++)
            if (!strcasecmp(mn, names[i])) { subop = i; break; }
        int rd = need_reg(toks[1]);
        int ra = need_reg(toks[2]);
        int rb = need_reg(toks[3]);
        /* [7:4] encodes Rd (destination=source-a position), [3:0] = Rb
         * The architecture description says Rd_Ra in the same nibble which means
         * the destination register and Ra share the same 4-bit field.
         * Per the worked example ADD R1,R1,R2 = 0x0012:
         *   [15:12]=0, [11:8]=0, [7:4]=1 (R1=Rd=Ra), [3:0]=2 (Rb=R2)
         * So Rd must equal Ra in the hardware layout -- assembler encodes Rd */
        if (rd != ra) warn("%s: Rd must equal Ra in hardware (Rd_Ra field); encoding Rd=%d", mn, rd);
        EMIT(mk_rrr(0x0, subop, rd, rb));
        return;
    }

    /* --- ALU_IMM (primary 0x1): ADDI SUBI ANDI ORI XORI CMPI --- */
    if (!strcasecmp(mn, "ADDI") || !strcasecmp(mn, "SUBI") ||
        !strcasecmp(mn, "ANDI") || !strcasecmp(mn, "ORI")  ||
        !strcasecmp(mn, "XORI") || !strcasecmp(mn, "CMPI")) {
        if (ntok < 3) err("%s Rd, imm", mn);
        static const char *inames[] = {"ADDI","SUBI","ANDI","ORI","XORI","CMPI"};
        int subop = -1;
        for (int i = 0; i < 6; i++)
            if (!strcasecmp(mn, inames[i])) { subop = i; break; }
        int rd = need_reg(toks[1]);
        int32_t imm; int have_imm = parse_imm(toks[2], &imm);
        if (!have_imm) {
            if (pass == PASS2) err("undefined immediate: %s", toks[2]);
            imm = 0;
        }
        if (imm < -8 || imm > 15) {
            /* emit EXT word before the instruction (EXT precedes base word) */
            int32_t hi12 = (imm >> 4) & 0xFFF;
            EMIT(mk_ext((int)hi12));
        }
        EMIT(mk_rri(0x1, subop, rd, (int)(imm & 0xF)));
        return;
    }

    /* --- SHIFT_ROTATE (primary 0x2): LSL LSR ASR ROL ROR --- */
    if (!strcasecmp(mn, "LSL") || !strcasecmp(mn, "LSR") ||
        !strcasecmp(mn, "ASR") || !strcasecmp(mn, "ROL") ||
        !strcasecmp(mn, "ROR")) {
        if (ntok < 3) err("%s Rd, count/Rs", mn);
        static const char *snames[] = {"LSL","LSR","ASR","ROL","ROR"};
        int subop = -1;
        for (int i = 0; i < 5; i++)
            if (!strcasecmp(mn, snames[i])) { subop = i; break; }
        int rd = need_reg(toks[1]);
        /* count can be register or immediate */
        int rs = parse_reg(toks[2]);
        int count = 0;
        if (rs < 0) {
            int32_t cv; if (!parse_imm(toks[2], &cv)) err("bad shift count");
            count = (int)(cv & 0xF);
        } else {
            count = rs;
        }
        EMIT(mk_rrr(0x2, subop, rd, count));
        return;
    }

    /* --- MULDIV (primary 0x3): MUL MULH MAC MAS DIVSTEP DIV --- */
    if (!strcasecmp(mn, "MUL")  || !strcasecmp(mn, "MULH") ||
        !strcasecmp(mn, "MAC")  || !strcasecmp(mn, "MAS")  ||
        !strcasecmp(mn, "DIVSTEP") || !strcasecmp(mn, "DIV")) {
        if (ntok < 4) err("%s dst, Ra, Rb", mn);
        static const char *mnames[] = {"MUL","MULH","MAC","MAS","DIVSTEP","DIV"};
        int subop = -1;
        for (int i = 0; i < 6; i++)
            if (!strcasecmp(mn, mnames[i])) { subop = i; break; }
        int rd = need_reg(toks[1]);
        int ra = need_reg(toks[2]);
        int rb = need_reg(toks[3]);
        (void)ra; /* Ra encoded in Rd_Ra field = rd */
        EMIT(mk_rrr(0x3, subop, rd, rb));
        return;
    }

    /* --- DSP_REDUCE (primary 0x4): REDUCE.* --- */
    /* Syntax: REDUCE.ADD A0/A1, src [, fold] [, local] */
    if (!strncasecmp(mn, "REDUCE.", 7)) {
        static const char *rnames[] =
            {"ADD","AND","OR","XOR","MIN","MAX","ABSMAX","COUNT"};
        int subop = -1;
        const char *op = mn + 7;
        for (int i = 0; i < 8; i++)
            if (!strcasecmp(op, rnames[i])) { subop = i; break; }
        if (subop < 0) err("unknown REDUCE operation: %s", op);
        if (ntok < 3) err("REDUCE.%s acc, src [,fold] [,local]", op);
        /* acc: A0 or A1 */
        int acc_sel = 0;
        if (!strcasecmp(toks[1], "A1")) acc_sel = 1;
        else if (strcasecmp(toks[1], "A0")) err("expected A0 or A1");
        int src = need_reg(toks[2]);
        int fold = 0, local_f = 0;
        for (int i = 3; i < ntok; i++) {
            if (!strcasecmp(toks[i], "fold"))    fold    = 1;
            if (!strcasecmp(toks[i], "local"))   local_f = 1;
        }
        EMIT(mk_dsp_red(subop, acc_sel, src, fold, local_f));
        return;
    }

    /* --- DOT (primary 0x4, subop 8) --- */
    if (!strcasecmp(mn, "DOT")) {
        if (ntok < 4) err("DOT acc, src0, src1");
        int acc_sel = (!strcasecmp(toks[1], "A1")) ? 1 : 0;
        int src0 = need_reg(toks[2]);
        int src1 = need_reg(toks[3]);
        int fold = 0, local_f = 0;
        for (int i = 4; i < ntok; i++) {
            if (!strcasecmp(toks[i], "fold"))  fold    = 1;
            if (!strcasecmp(toks[i], "local")) local_f = 1;
        }
        (void)fold; (void)local_f;
        /* base word + mandatory EXT for src1 */
        uint16_t base = FIELD(0x4,15,12)|FIELD(8,11,8)|FIELD(acc_sel,7,7)|FIELD(src0,6,3);
        EMIT(base);
        EMIT(mk_ext(src1 & 0xF));
        return;
    }

    /* --- SAD (primary 0x4, subop 9) --- */
    if (!strcasecmp(mn, "SAD")) {
        if (ntok < 4) err("SAD acc, src0, src1");
        int acc_sel = (!strcasecmp(toks[1], "A1")) ? 1 : 0;
        int src0 = need_reg(toks[2]);
        int src1 = need_reg(toks[3]);
        uint16_t base = FIELD(0x4,15,12)|FIELD(9,11,8)|FIELD(acc_sel,7,7)|FIELD(src0,6,3);
        EMIT(base);
        EMIT(mk_ext(src1 & 0xF));
        return;
    }

    /* --- PACK_SHUFFLE (primary 0x5) --- */
    if (!strcasecmp(mn, "PACK")   || !strcasecmp(mn, "UNPACK") ||
        !strcasecmp(mn, "ZIP")    || !strcasecmp(mn, "UNZIP")  ||
        !strcasecmp(mn, "BSWAP")  || !strcasecmp(mn, "WSWAP")  ||
        !strcasecmp(mn, "SHUFFLE")|| !strcasecmp(mn, "MOV")    ||
        !strcasecmp(mn, "ZEXT8")  || !strcasecmp(mn, "SEXT8")  ||
        !strcasecmp(mn, "ZEXT16") || !strcasecmp(mn, "SEXT16")) {
        static const char *pnames[] =
            {"PACK","UNPACK","ZIP","UNZIP","BSWAP","WSWAP","SHUFFLE","MOV",
             "ZEXT8","SEXT8","ZEXT16","SEXT16"};
        int subop = -1;
        for (int i = 0; i < 12; i++)
            if (!strcasecmp(mn, pnames[i])) { subop = i; break; }
        int rd = need_reg(toks[1]);
        int rs = (ntok >= 3) ? need_reg(toks[2]) : 0;
        EMIT(mk_rrr(0x5, subop, rd, rs));
        return;
    }

    /* --- LOAD (primary 0x6): LD Rd, [base+offset] --- */
    if (!strcasecmp(mn, "LD") || !strcasecmp(mn, "LDW") ||
        !strcasecmp(mn, "LDB") || !strcasecmp(mn, "LDH")) {
        if (ntok < 3) err("%s Rd, [base+offset]", mn);
        /* detect width from mnemonic suffix; default word=0 */
        int mode_width = 0; /* 0=word(32), subop-like */
        int rd = need_reg(toks[1]);
        int base_r, reg_off;
        int32_t imm_off;
        parse_mem(toks[2], &base_r, &reg_off, &imm_off);
        /* [11:8] = mode_width, [7:4] = Rd, [3:0] = base_r
         * if offset, emit EXT word before with offset in payload */
        if (imm_off != 0 || reg_off >= 0) {
            int ext_payload = (reg_off >= 0) ? reg_off : (int)(imm_off & 0xFFF);
            EMIT(mk_ext(ext_payload));
        }
        EMIT(FIELD(0x6,15,12)|FIELD(mode_width,11,8)|FIELD(rd,7,4)|FIELD(base_r,3,0));
        return;
    }

    /* --- STORE (primary 0x7): ST Rs, [base+offset] --- */
    if (!strcasecmp(mn, "ST") || !strcasecmp(mn, "STW") ||
        !strcasecmp(mn, "STB") || !strcasecmp(mn, "STH")) {
        if (ntok < 3) err("%s Rs, [base+offset]", mn);
        int mode_width = 0;
        int rs = need_reg(toks[1]);
        int base_r, reg_off;
        int32_t imm_off;
        parse_mem(toks[2], &base_r, &reg_off, &imm_off);
        if (imm_off != 0 || reg_off >= 0) {
            int ext_payload = (reg_off >= 0) ? reg_off : (int)(imm_off & 0xFFF);
            EMIT(mk_ext(ext_payload));
        }
        EMIT(FIELD(0x7,15,12)|FIELD(mode_width,11,8)|FIELD(rs,7,4)|FIELD(base_r,3,0));
        return;
    }

    /* --- BRANCH_COND (primary 0x8): B.EQ B.NE B.LT B.GE B.LTU B.GEU B.MI B.PL --- */
    if (!strncasecmp(mn, "B.", 2)) {
        static const char *bcnames[] = {"EQ","NE","LT","GE","LTU","GEU","MI","PL"};
        int cond = -1;
        const char *suf = mn + 2;
        for (int i = 0; i < 8; i++)
            if (!strcasecmp(suf, bcnames[i])) { cond = i; break; }
        if (cond < 0) err("unknown branch condition: %s", mn);
        if (ntok < 2) err("%s target", mn);
        int32_t target = 0;
        if (!parse_imm(toks[1], &target)) {
            if (pass == PASS2) err("undefined branch target: %s", toks[1]);
        }
        /* disp8 = (target - (org+2)) / 2 — word-relative, PC-relative after fetch */
        int32_t disp = ((int32_t)target - (int32_t)(org + 2)) / 2;
        if (pass == PASS2 && (disp < -128 || disp > 127)) {
            /* emit EXT word for extended branch */
            EMIT(mk_ext((int)(disp >> 8) & 0xFFF));
        } else if (pass == PASS1) {
            /* conservative: reserve space for possible EXT (won't cause
               infinite loop since we don't renegotiate sizes) */
        }
        EMIT(mk_br(cond, (int)(disp & 0xFF)));
        return;
    }

    /* --- CONTROL_FLOW (primary 0x9) --- */
    /* CALL target  — PC-relative */
    if (!strcasecmp(mn, "CALL")) {
        if (ntok < 2) err("CALL target");
        int32_t target = 0;
        if (!parse_imm(toks[1], &target)) {
            if (pass == PASS2) err("undefined call target: %s", toks[1]);
        }
        int32_t disp = ((int32_t)target - (int32_t)(org + 2)) / 2;
        if (pass == PASS2 && (disp < -128 || disp > 127))
            EMIT(mk_ext((int)(disp >> 8) & 0xFFF));
        EMIT(mk_ctrl(0, (int)(disp & 0xFF)));
        return;
    }
    /* JMP target — PC-relative */
    if (!strcasecmp(mn, "JMP")) {
        if (ntok < 2) err("JMP target");
        int32_t target = 0;
        if (!parse_imm(toks[1], &target)) {
            if (pass == PASS2) err("undefined jump target: %s", toks[1]);
        }
        int32_t disp = ((int32_t)target - (int32_t)(org + 2)) / 2;
        if (pass == PASS2 && (disp < -128 || disp > 127))
            EMIT(mk_ext((int)(disp >> 8) & 0xFFF));
        EMIT(mk_ctrl(1, (int)(disp & 0xFF)));
        return;
    }
    /* RET */
    if (!strcasecmp(mn, "RET")) {
        EMIT(mk_ctrl(2, 0));
        return;
    }
    /* JMPR Rs — register indirect */
    if (!strcasecmp(mn, "JMPR")) {
        if (ntok < 2) err("JMPR Rs");
        int rs = need_reg(toks[1]);
        EMIT(FIELD(0x9,15,12)|FIELD(3,11,8)|FIELD(rs,3,0));
        return;
    }

    /* --- STACK (primary 0xA) --- */
    if (!strcasecmp(mn, "PUSH")) {
        if (ntok < 2) err("PUSH Reg");
        int rs = need_reg(toks[1]);
        EMIT(mk_stack(0, rs));
        return;
    }
    if (!strcasecmp(mn, "POP")) {
        if (ntok < 2) err("POP Reg");
        int rd = need_reg(toks[1]);
        EMIT(mk_stack(1, rd));
        return;
    }
    /* PUSHM mask — 16-bit register mask; uses EXT word */
    if (!strcasecmp(mn, "PUSHM")) {
        if (ntok < 2) err("PUSHM mask");
        int32_t mask = need_imm(toks[1]);
        EMIT(mk_ext((int)(mask & 0xFFF)));       /* low 12 bits in EXT */
        EMIT(mk_stack(2, 0));
        return;
    }
    if (!strcasecmp(mn, "POPM")) {
        if (ntok < 2) err("POPM mask");
        int32_t mask = need_imm(toks[1]);
        EMIT(mk_ext((int)(mask & 0xFFF)));
        EMIT(mk_stack(3, 0));
        return;
    }

    /* --- STREAM (primary 0xB) --- */
    /* General stream ops: QMASK QPEEK QPUSH QPOP QDUP QREPL QCIRC
       Syntax: QXXX Q0/Q1, arg  */
    {
        static const char *qnames[] =
            {"QMASK","QPEEK","QPUSH","QPOP","QDUP","QREPL",NULL,"QCIRC"};
        /* subops 0-5, 7 */
        static const int qsubops[] = {0,1,2,3,4,5,-1,7};
        for (int i = 0; i < 8; i++) {
            if (!qnames[i]) continue;
            if (!strcasecmp(mn, qnames[i])) {
                if (ntok < 3) err("%s Q0/Q1, arg", mn);
                int q = (!strcasecmp(toks[1],"Q1")) ? 1 : 0;
                int32_t arg = need_imm(toks[2]);
                /* select[7:6]: bit7=reserved, bit6=queue_sel */
                int select = q & 1;
                EMIT(mk_stream(qsubops[i], select, (int)(arg & 0x3F)));
                goto done;
            }
        }
    }

    /* QCFG Qn, field, Rs/imm
       [15:12]=0xB [11:8]=6 [7]=Qn [6:4]=field [3:0]=0 + EXT for value */
    if (!strcasecmp(mn, "QCFG")) {
        if (ntok < 4) err("QCFG Q0/Q1, field, Rs/imm");
        int qn = (!strcasecmp(toks[1],"Q1")) ? 1 : 0;
        /* field name or number */
        static const char *fnames[] =
            {"ADDR","INNER_STRIDE","INNER_COUNT","OUTER_ADJUST","OUTER_COUNT","WIDTH","END_MODE"};
        int field_idx = -1;
        int32_t fv;
        if (parse_imm(toks[2], &fv)) {
            field_idx = (int)fv;
        } else {
            for (int i = 0; i < 7; i++)
                if (!strcasecmp(toks[2], fnames[i])) { field_idx = i; break; }
            if (field_idx < 0) err("unknown QCFG field: %s", toks[2]);
        }
        int rs_or_imm = need_reg(toks[3]);
        if (rs_or_imm < 0) { int32_t v = need_imm(toks[3]); rs_or_imm = (int)(v & 0xF); }
        /* base word */
        uint16_t base = FIELD(0xB,15,12)|FIELD(6,11,8)|FIELD(qn,7,7)|FIELD(field_idx,6,4);
        EMIT(base);
        EMIT(mk_ext(rs_or_imm & 0xF));
        goto done;
    }

    /* QSTEP Qn */
    if (!strcasecmp(mn, "QSTEP")) {
        if (ntok < 2) err("QSTEP Qn");
        int qn = (!strcasecmp(toks[1],"Q1")) ? 1 : 0;
        EMIT(FIELD(0xB,15,12)|FIELD(8,11,8)|FIELD(qn,7,4));
        goto done;
    }

    /* --- LOOP_AGU (primary 0xC) --- */
    /* LOOPSET count, LOOPEND, AGUCFG args, STRIDE args */
    if (!strcasecmp(mn, "LOOPSET")) {
        int32_t cnt = (ntok >= 2) ? need_imm(toks[1]) : 0;
        EMIT(mk_loop(0, (int)(cnt & 0xFF)));
        return;
    }
    if (!strcasecmp(mn, "LOOPEND")) {
        EMIT(mk_loop(1, 0));
        return;
    }
    if (!strcasecmp(mn, "AGUCFG")) {
        int32_t args = (ntok >= 2) ? need_imm(toks[1]) : 0;
        EMIT(mk_loop(2, (int)(args & 0xFF)));
        return;
    }
    if (!strcasecmp(mn, "STRIDE")) {
        int32_t args = (ntok >= 2) ? need_imm(toks[1]) : 0;
        EMIT(mk_loop(3, (int)(args & 0xFF)));
        return;
    }

    /* --- SYSTEM (primary 0xD) --- */
    /* MRS Rd, sysreg  — read system register */
    if (!strcasecmp(mn, "MRS")) {
        if (ntok < 3) err("MRS Rd, sysreg");
        int rd = need_reg(toks[1]);
        int32_t sreg = need_imm(toks[2]);
        EMIT(mk_system(0, (int)((rd << 4) | (sreg & 0xF))));
        return;
    }
    /* MSR sysreg, Rs */
    if (!strcasecmp(mn, "MSR")) {
        if (ntok < 3) err("MSR sysreg, Rs");
        int32_t sreg = need_imm(toks[1]);
        int rs = need_reg(toks[2]);
        EMIT(mk_system(1, (int)((rs << 4) | (sreg & 0xF))));
        return;
    }
    if (!strcasecmp(mn, "EI"))      { EMIT(mk_system(2, 0)); return; }
    if (!strcasecmp(mn, "DI"))      { EMIT(mk_system(3, 0)); return; }
    if (!strcasecmp(mn, "IRET"))    { EMIT(mk_system(4, 0)); return; }
    /* ASCALL imm */
    if (!strcasecmp(mn, "ASCALL")) {
        int32_t v = (ntok >= 2) ? need_imm(toks[1]) : 0;
        EMIT(mk_system(5, (int)(v & 0xFF)));
        return;
    }
    /* TIMERLOAD Rs */
    if (!strcasecmp(mn, "TIMERLOAD")) {
        int rs = (ntok >= 2) ? need_reg(toks[1]) : 0;
        EMIT(mk_system(6, rs & 0xFF));
        return;
    }
    /* TIMERVEC Rs */
    if (!strcasecmp(mn, "TIMERVEC")) {
        int rs = (ntok >= 2) ? need_reg(toks[1]) : 0;
        EMIT(mk_system(7, rs & 0xFF));
        return;
    }
    /* TIMERCTL imm */
    if (!strcasecmp(mn, "TIMERCTL")) {
        int32_t v = (ntok >= 2) ? need_imm(toks[1]) : 0;
        EMIT(mk_system(8, (int)(v & 0xFF)));
        return;
    }
    /* RDCYCLE Rd */
    if (!strcasecmp(mn, "RDCYCLE")) {
        int rd = (ntok >= 2) ? need_reg(toks[1]) : 0;
        EMIT(mk_system(9, rd & 0xFF));
        return;
    }
    /* MODE mode */
    if (!strcasecmp(mn, "MODE")) {
        if (ntok < 2) err("MODE mode");
        static const char *mode_names[] =
            {"SCALAR32","PACKED16","PACKED8","LOW16","LOW8","PAIRED64"};
        int mode_code = -1;
        int32_t mv;
        if (parse_imm(toks[1], &mv)) {
            mode_code = (int)mv;
        } else {
            for (int i = 0; i < 6; i++)
                if (!strcasecmp(toks[1], mode_names[i])) { mode_code = i; break; }
            if (mode_code < 0) err("unknown mode: %s", toks[1]);
        }
        EMIT(FIELD(0xD,15,12)|FIELD(10,11,8)|FIELD(mode_code,7,5));
        return;
    }
    if (!strcasecmp(mn, "WFI"))  { EMIT(mk_system(11, 0)); return; }
    if (!strcasecmp(mn, "WFE"))  { EMIT(mk_system(12, 0)); return; }
    if (!strcasecmp(mn, "HALT")) { EMIT(mk_system(13, 0)); return; }
    /* CTXSAVE Rbase, mask   — mask + mandatory EXT for Rbase */
    if (!strcasecmp(mn, "CTXSAVE")) {
        if (ntok < 3) err("CTXSAVE Rbase, mask");
        int rbase = need_reg(toks[1]);
        int32_t mask = need_imm(toks[2]);
        EMIT(mk_system(14, (int)(mask & 0xFF)));
        EMIT(mk_ext(rbase & 0xF));
        return;
    }
    if (!strcasecmp(mn, "CTXRESTORE")) {
        if (ntok < 3) err("CTXRESTORE Rbase, mask");
        int rbase = need_reg(toks[1]);
        int32_t mask = need_imm(toks[2]);
        EMIT(mk_system(15, (int)(mask & 0xFF)));
        EMIT(mk_ext(rbase & 0xF));
        return;
    }

    /* --- pseudo-instructions / aliases --- */
    /* NOP = ADDI R0, 0  (no flags on R0 read) */
    if (!strcasecmp(mn, "NOP")) {
        EMIT(mk_rri(0x1, 0, 0, 0));  /* ADDI R0, 0 */
        return;
    }
    /* LI Rd, imm  — load immediate: ADDI Rd, imm (with EXT if needed) */
    if (!strcasecmp(mn, "LI")) {
        if (ntok < 3) err("LI Rd, imm");
        int rd = need_reg(toks[1]);
        int32_t imm = 0;
        if (!parse_imm(toks[2], &imm) && pass == PASS2)
            err("undefined immediate: %s", toks[2]);
        if (imm < -8 || imm > 15)
            EMIT(mk_ext((int)((imm >> 4) & 0xFFF)));
        EMIT(mk_rri(0x1, 0, rd, (int)(imm & 0xF)));
        return;
    }
    /* MVR Rd, Rs  — alias for MOV */
    if (!strcasecmp(mn, "MVR")) {
        if (ntok < 3) err("MVR Rd, Rs");
        int rd = need_reg(toks[1]);
        int rs = need_reg(toks[2]);
        EMIT(mk_rrr(0x5, 7, rd, rs));
        return;
    }

    err("unknown mnemonic: '%s'", mn);
done:
    return;
}

/* ───────────────────────── output writers ──────────────────── */

static void write_bin(FILE *f) {
    for (int i = 0; i < nwords; i++) {
        uint8_t lo = words[i] & 0xFF;
        uint8_t hi = (words[i] >> 8) & 0xFF;
        fputc(lo, f);
        fputc(hi, f);
    }
}

static void write_vhex(FILE *f) {
    for (int i = 0; i < nwords; i++)
        fprintf(f, "%04x\n", words[i]);
}

/* Intel HEX writer */
static void ihex_record(FILE *f, uint8_t type, uint32_t addr,
                        const uint8_t *data, int len) {
    uint8_t cksum = (uint8_t)(len + (addr >> 8) + (addr & 0xFF) + type);
    fprintf(f, ":%02X%04X%02X", len, addr & 0xFFFF, type);
    for (int i = 0; i < len; i++) { fprintf(f, "%02X", data[i]); cksum += data[i]; }
    fprintf(f, "%02X\n", (uint8_t)(~cksum + 1));
}

static void write_ihex(FILE *f) {
    uint8_t buf[32];
    int byte_count = nwords * 2;
    int pos = 0;
    uint32_t base_addr = 0; /* track extended linear address */
    while (pos < byte_count) {
        uint32_t byte_addr = (uint32_t)pos;
        /* emit extended linear address record if needed */
        if ((byte_addr >> 16) != base_addr) {
            base_addr = byte_addr >> 16;
            uint8_t ea[2] = { (uint8_t)(base_addr >> 8), (uint8_t)(base_addr) };
            ihex_record(f, 4, 0, ea, 2);
        }
        int chunk = byte_count - pos;
        if (chunk > 16) chunk = 16;
        for (int i = 0; i < chunk; i++) {
            int wi = (pos + i) / 2;
            buf[i] = (pos + i) % 2 == 0
                     ? (uint8_t)(words[wi] & 0xFF)
                     : (uint8_t)((words[wi] >> 8) & 0xFF);
        }
        ihex_record(f, 0, byte_addr & 0xFFFF, buf, chunk);
        pos += chunk;
    }
    /* EOF record */
    ihex_record(f, 1, 0, NULL, 0);
}

/* ───────────────────────── main ──────────────────────────── */

typedef enum { FMT_BIN, FMT_HEX, FMT_VHEX } OutFmt;

int main(int argc, char *argv[]) {
    const char *infile  = NULL;
    const char *outfile = NULL;
    OutFmt fmt = FMT_BIN;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-o") && i+1 < argc) { outfile = argv[++i]; }
        else if (!strcmp(argv[i], "-f") && i+1 < argc) {
            i++;
            if      (!strcmp(argv[i], "bin"))  fmt = FMT_BIN;
            else if (!strcmp(argv[i], "hex"))  fmt = FMT_HEX;
            else if (!strcmp(argv[i], "vhex")) fmt = FMT_VHEX;
            else die("unknown format '%s' (bin|hex|vhex)", argv[i]);
        }
        else if (argv[i][0] == '-') die("unknown option '%s'", argv[i]);
        else infile = argv[i];
    }
    if (!infile) die("no input file\nusage: aurora_asm [-o out] [-f bin|hex|vhex] in.asm");

    /* read entire input file */
    FILE *fin = fopen(infile, "r");
    if (!fin) die("cannot open '%s': %s", infile, strerror(errno));

    /* store lines */
    static char *lines[MAX_LINES];
    static char  linebuf[MAX_LINES][MAX_LINE_LEN];
    int nlines = 0;
    while (nlines < MAX_LINES && fgets(linebuf[nlines], MAX_LINE_LEN, fin)) {
        /* strip trailing newline */
        char *nl = strrchr(linebuf[nlines], '\n');
        if (nl) *nl = '\0';
        lines[nlines] = linebuf[nlines];
        nlines++;
    }
    fclose(fin);

    /* pass 1 — define labels */
    pass = PASS1;
    org  = 0;
    memset(words, 0, sizeof(words));
    nwords = 0;
    for (int i = 0; i < nlines; i++) {
        lineno = i + 1;
        char tmp[MAX_LINE_LEN];
        snprintf(tmp, MAX_LINE_LEN, "%s", lines[i]);
        assemble_line(tmp);
    }

    /* pass 2 — emit code */
    pass = PASS2;
    org  = 0;
    memset(words, 0, sizeof(words));
    nwords = 0;
    for (int i = 0; i < nlines; i++) {
        lineno = i + 1;
        char tmp[MAX_LINE_LEN];
        snprintf(tmp, MAX_LINE_LEN, "%s", lines[i]);
        assemble_line(tmp);
    }

    /* write output */
    FILE *fout = outfile ? fopen(outfile, "wb") : stdout;
    if (!fout) die("cannot open output '%s': %s", outfile, strerror(errno));

    if (fmt == FMT_VHEX || fmt == FMT_HEX) {
        /* reopen in text mode */
        if (outfile) { fclose(fout); fout = fopen(outfile, "w"); }
        if (!fout) die("cannot open output '%s': %s", outfile, strerror(errno));
    }

    switch (fmt) {
        case FMT_BIN:  write_bin(fout);  break;
        case FMT_HEX:  write_ihex(fout); break;
        case FMT_VHEX: write_vhex(fout); break;
    }

    if (fout != stdout) fclose(fout);

    fprintf(stderr, "aurora_asm: assembled %d word(s) (%d bytes)\n",
            nwords, nwords * 2);
    return 0;
}
