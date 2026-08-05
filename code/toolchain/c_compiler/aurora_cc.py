#!/usr/bin/env python3
"""
Aurora C Compiler  —  aurora_cc.py
Compiles a subset of C to Aurora v1.2 assembly (text mnemonics).

Supported C subset
------------------
  Types        : int (32-bit signed), void
  Declarations : global int variables, function definitions with int/void params
  Statements   : if/else, while, for, return, expression-statement, block
  Expressions  : integer literals, variable references, assignment (=),
                 arithmetic  (+ - * / %),
                 bitwise     (& | ^ ~ << >>),
                 logical     (&& || !),
                 comparison  (== != < <= > >=),
                 unary minus, pre/post ++ --,
                 function calls (no varargs)
  Initializers : int x = expr;  inside functions and at file scope

Calling convention  (Aurora ABI)
---------------------------------
  R0–R3   : first four integer arguments / return value in R0
  R4–R7   : caller-saved temporaries
  R8–R12  : callee-saved (saved/restored by callee if used)
  R13     : link register  (CALL stores return address here)
  R14     : stack pointer  (SP), grows downward
  R15     : program counter (not addressable as GPR in this compiler)

Stack frame layout
------------------
  [SP + frame_size - 4]  param 0 / first local
  [SP + frame_size - 8]  param 1 / second local
  ...
  [SP + 0]               last local
  SP points to top (lowest address) of the frame.
  The prologue subtracts frame_size from SP once; the epilogue restores it.

Usage
-----
  python3 aurora_cc.py input.c [-o output.s]
"""

import sys
import re
import os
import argparse
from typing import List, Optional, Dict, Tuple


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

TK_INT_KW   = 'int'
TK_VOID_KW  = 'void'
TK_IF       = 'if'
TK_ELSE     = 'else'
TK_WHILE    = 'while'
TK_FOR      = 'for'
TK_RETURN   = 'return'
TK_IDENT    = 'IDENT'
TK_NUMBER   = 'NUMBER'
TK_PLUS     = '+'
TK_MINUS    = '-'
TK_STAR     = '*'
TK_SLASH    = '/'
TK_PERCENT  = '%'
TK_AMP      = '&'
TK_PIPE     = '|'
TK_CARET    = '^'
TK_TILDE    = '~'
TK_LSHIFT   = '<<'
TK_RSHIFT   = '>>'
TK_EQ       = '=='
TK_NEQ      = '!='
TK_LT       = '<'
TK_LE       = '<='
TK_GT       = '>'
TK_GE       = '>='
TK_AND      = '&&'
TK_OR       = '||'
TK_NOT      = '!'
TK_ASSIGN   = '='
TK_PLUSEQ   = '+='
TK_MINUSEQ  = '-='
TK_STAREQ   = '*='
TK_SLASHEQ  = '/='
TK_PERCENTEQ= '%='
TK_AMPEQ    = '&='
TK_PIPEEQ   = '|='
TK_CARETEQ  = '^='
TK_LSHIFTEQ = '<<='
TK_RSHIFTEQ = '>>='
TK_PLUSPLUS = '++'
TK_MINUSMINUS = '--'
TK_LPAREN   = '('
TK_RPAREN   = ')'
TK_LBRACE   = '{'
TK_RBRACE   = '}'
TK_SEMICOL  = ';'
TK_COMMA    = ','
TK_EOF      = 'EOF'

KEYWORDS = {'int', 'void', 'if', 'else', 'while', 'for', 'return'}

Token = Tuple[str, object, int]  # (type, value, line)


def lex(src: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    line = 1
    n = len(src)
    while i < n:
        if src[i] in ' \t\r':
            i += 1; continue
        if src[i] == '\n':
            line += 1; i += 1; continue
        if src[i:i+2] == '//':
            while i < n and src[i] != '\n': i += 1
            continue
        if src[i:i+2] == '/*':
            i += 2
            while i < n - 1 and src[i:i+2] != '*/':
                if src[i] == '\n': line += 1
                i += 1
            i += 2; continue
        if src[i].isdigit():
            j = i
            if src[i:i+2] in ('0x', '0X'):
                j = i + 2
                while j < n and src[j] in '0123456789abcdefABCDEF': j += 1
                tokens.append((TK_NUMBER, int(src[i:j], 16), line))
            else:
                while j < n and src[j].isdigit(): j += 1
                tokens.append((TK_NUMBER, int(src[i:j]), line))
            i = j; continue
        if src[i].isalpha() or src[i] == '_':
            j = i
            while j < n and (src[j].isalnum() or src[j] == '_'): j += 1
            word = src[i:j]
            tokens.append((word if word in KEYWORDS else TK_IDENT, word, line))
            i = j; continue
        three = src[i:i+3]
        if three == '<<=': tokens.append((TK_LSHIFTEQ, '<<=', line)); i += 3; continue
        if three == '>>=': tokens.append((TK_RSHIFTEQ, '>>=', line)); i += 3; continue
        two = src[i:i+2]
        MAP2 = {'<<':TK_LSHIFT,'>>':TK_RSHIFT,'==':TK_EQ,'!=':TK_NEQ,
                '<=':TK_LE,'>=':TK_GE,'&&':TK_AND,'||':TK_OR,
                '++':TK_PLUSPLUS,'--':TK_MINUSMINUS,
                '+=':TK_PLUSEQ,'-=':TK_MINUSEQ,'*=':TK_STAREQ,
                '/=':TK_SLASHEQ,'%=':TK_PERCENTEQ,
                '&=':TK_AMPEQ,'|=':TK_PIPEEQ,'^=':TK_CARETEQ}
        if two in MAP2: tokens.append((MAP2[two], two, line)); i += 2; continue
        MAP1 = {'+':TK_PLUS,'-':TK_MINUS,'*':TK_STAR,'/':TK_SLASH,
                '%':TK_PERCENT,'&':TK_AMP,'|':TK_PIPE,'^':TK_CARET,
                '~':TK_TILDE,'<':TK_LT,'>':TK_GT,'!':TK_NOT,
                '=':TK_ASSIGN,'(':TK_LPAREN,')':TK_RPAREN,
                '{':TK_LBRACE,'}':TK_RBRACE,';':TK_SEMICOL,',':TK_COMMA}
        if src[i] in MAP1: tokens.append((MAP1[src[i]], src[i], line)); i += 1; continue
        raise SyntaxError(f"Unknown character {src[i]!r} at line {line}")
    tokens.append((TK_EOF, None, line))
    return tokens


# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------

class Node: pass

class Program(Node):
    def __init__(self, decls): self.decls = decls

class GlobalVar(Node):
    def __init__(self, name, init=None):
        self.name = name; self.init = init

class FuncDef(Node):
    def __init__(self, ret_type, name, params, body):
        self.ret_type = ret_type; self.name = name
        self.params = params; self.body = body

class Block(Node):
    def __init__(self, stmts): self.stmts = stmts

class VarDecl(Node):
    def __init__(self, name, init=None):
        self.name = name; self.init = init

class IfStmt(Node):
    def __init__(self, cond, then_, else_=None):
        self.cond = cond; self.then_ = then_; self.else_ = else_

class WhileStmt(Node):
    def __init__(self, cond, body):
        self.cond = cond; self.body = body

class ForStmt(Node):
    def __init__(self, init, cond, step, body):
        self.init = init; self.cond = cond
        self.step = step; self.body = body

class ReturnStmt(Node):
    def __init__(self, expr=None): self.expr = expr

class ExprStmt(Node):
    def __init__(self, expr): self.expr = expr

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op; self.left = left; self.right = right

class UnaryOp(Node):
    def __init__(self, op, operand, post=False):
        self.op = op; self.operand = operand; self.post = post

class Assign(Node):
    def __init__(self, op, target, value):
        self.op = op; self.target = target; self.value = value

class Ident(Node):
    def __init__(self, name): self.name = name

class Literal(Node):
    def __init__(self, value): self.value = value

class Call(Node):
    def __init__(self, name, args):
        self.name = name; self.args = args


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0

    def peek(self): return self.tokens[self.pos]
    def peek_type(self): return self.tokens[self.pos][0]

    def consume(self, expected=None):
        tok = self.tokens[self.pos]
        if expected is not None and tok[0] != expected:
            raise SyntaxError(f"Line {tok[2]}: expected {expected!r}, got {tok[0]!r} ({tok[1]!r})")
        self.pos += 1; return tok

    def match(self, *types): return self.peek_type() in types

    def parse_program(self):
        decls = []
        while not self.match(TK_EOF):
            decls.append(self.parse_top_level())
        return Program(decls)

    def parse_top_level(self):
        type_tok = self.consume()
        if type_tok[0] not in (TK_INT_KW, TK_VOID_KW):
            raise SyntaxError(f"Line {type_tok[2]}: expected type")
        ret_type = type_tok[1]
        name = self.consume(TK_IDENT)[1]
        if self.match(TK_LPAREN):
            self.consume(TK_LPAREN)
            params = []
            if not self.match(TK_RPAREN):
                while True:
                    pt = self.consume()
                    if pt[0] not in (TK_INT_KW, TK_VOID_KW):
                        raise SyntaxError(f"Line {pt[2]}: expected param type")
                    pn = self.consume(TK_IDENT)
                    params.append((pt[1], pn[1]))
                    if not self.match(TK_COMMA): break
                    self.consume(TK_COMMA)
            self.consume(TK_RPAREN)
            body = self.parse_block()
            return FuncDef(ret_type, name, params, body)
        else:
            init = None
            if self.match(TK_ASSIGN):
                self.consume(TK_ASSIGN); init = self.consume(TK_NUMBER)[1]
            self.consume(TK_SEMICOL)
            return GlobalVar(name, init)

    def parse_block(self):
        self.consume(TK_LBRACE)
        stmts = []
        while not self.match(TK_RBRACE):
            stmts.append(self.parse_stmt())
        self.consume(TK_RBRACE)
        return Block(stmts)

    def parse_stmt(self):
        t = self.peek_type()
        if t == TK_INT_KW: return self.parse_var_decl()
        if t == TK_IF:     return self.parse_if()
        if t == TK_WHILE:  return self.parse_while()
        if t == TK_FOR:    return self.parse_for()
        if t == TK_RETURN: return self.parse_return()
        if t == TK_LBRACE: return self.parse_block()
        expr = self.parse_expr(); self.consume(TK_SEMICOL)
        return ExprStmt(expr)

    def parse_var_decl(self):
        self.consume(TK_INT_KW)
        name = self.consume(TK_IDENT)[1]
        init = None
        if self.match(TK_ASSIGN):
            self.consume(TK_ASSIGN); init = self.parse_expr()
        self.consume(TK_SEMICOL)
        return VarDecl(name, init)

    def parse_if(self):
        self.consume(TK_IF); self.consume(TK_LPAREN)
        cond = self.parse_expr(); self.consume(TK_RPAREN)
        then_ = self.parse_stmt()
        else_ = None
        if self.match(TK_ELSE):
            self.consume(TK_ELSE); else_ = self.parse_stmt()
        return IfStmt(cond, then_, else_)

    def parse_while(self):
        self.consume(TK_WHILE); self.consume(TK_LPAREN)
        cond = self.parse_expr(); self.consume(TK_RPAREN)
        return WhileStmt(cond, self.parse_stmt())

    def parse_for(self):
        self.consume(TK_FOR); self.consume(TK_LPAREN)
        if self.match(TK_SEMICOL):
            init = None; self.consume(TK_SEMICOL)
        elif self.match(TK_INT_KW):
            self.consume(TK_INT_KW)
            vname = self.consume(TK_IDENT)[1]
            vi = None
            if self.match(TK_ASSIGN):
                self.consume(TK_ASSIGN); vi = self.parse_expr()
            self.consume(TK_SEMICOL); init = VarDecl(vname, vi)
        else:
            init = ExprStmt(self.parse_expr()); self.consume(TK_SEMICOL)
        cond = Literal(1) if self.match(TK_SEMICOL) else self.parse_expr()
        self.consume(TK_SEMICOL)
        step = None if self.match(TK_RPAREN) else self.parse_expr()
        self.consume(TK_RPAREN)
        return ForStmt(init, cond, step, self.parse_stmt())

    def parse_return(self):
        self.consume(TK_RETURN)
        if self.match(TK_SEMICOL):
            self.consume(TK_SEMICOL); return ReturnStmt(None)
        expr = self.parse_expr(); self.consume(TK_SEMICOL)
        return ReturnStmt(expr)

    # Expressions — precedence climbing
    def parse_expr(self): return self.parse_assign()

    def parse_assign(self):
        left = self.parse_logical_or()
        ASSIGN_OPS = {TK_ASSIGN,TK_PLUSEQ,TK_MINUSEQ,TK_STAREQ,
                      TK_SLASHEQ,TK_PERCENTEQ,TK_AMPEQ,TK_PIPEEQ,
                      TK_CARETEQ,TK_LSHIFTEQ,TK_RSHIFTEQ}
        if self.peek_type() in ASSIGN_OPS:
            op = self.consume()[0]; right = self.parse_assign()
            return Assign(op, left, right)
        return left

    def _binop(self, sub, *ops):
        node = sub()
        while self.peek_type() in ops:
            op = self.consume()[0]; right = sub()
            node = BinOp(op, node, right)
        return node

    def parse_logical_or(self):    return self._binop(self.parse_logical_and, TK_OR)
    def parse_logical_and(self):   return self._binop(self.parse_bitwise_or,  TK_AND)
    def parse_bitwise_or(self):    return self._binop(self.parse_bitwise_xor, TK_PIPE)
    def parse_bitwise_xor(self):   return self._binop(self.parse_bitwise_and, TK_CARET)
    def parse_bitwise_and(self):   return self._binop(self.parse_equality,    TK_AMP)
    def parse_equality(self):      return self._binop(self.parse_relational,  TK_EQ, TK_NEQ)
    def parse_relational(self):    return self._binop(self.parse_shift,       TK_LT, TK_LE, TK_GT, TK_GE)
    def parse_shift(self):         return self._binop(self.parse_additive,    TK_LSHIFT, TK_RSHIFT)
    def parse_additive(self):      return self._binop(self.parse_multiplicative, TK_PLUS, TK_MINUS)
    def parse_multiplicative(self):return self._binop(self.parse_unary,       TK_STAR, TK_SLASH, TK_PERCENT)

    def parse_unary(self):
        t = self.peek_type()
        if t == TK_MINUS:      self.consume(); return UnaryOp('-',  self.parse_unary())
        if t == TK_TILDE:      self.consume(); return UnaryOp('~',  self.parse_unary())
        if t == TK_NOT:        self.consume(); return UnaryOp('!',  self.parse_unary())
        if t == TK_PLUSPLUS:   self.consume(); return UnaryOp('++', self.parse_unary(), post=False)
        if t == TK_MINUSMINUS: self.consume(); return UnaryOp('--', self.parse_unary(), post=False)
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            t = self.peek_type()
            if   t == TK_PLUSPLUS:   self.consume(); node = UnaryOp('++', node, post=True)
            elif t == TK_MINUSMINUS: self.consume(); node = UnaryOp('--', node, post=True)
            else: break
        return node

    def parse_primary(self):
        t = self.peek_type()
        if t == TK_NUMBER:
            return Literal(self.consume()[1])
        if t == TK_IDENT:
            name = self.consume()[1]
            if self.match(TK_LPAREN):
                self.consume(TK_LPAREN); args = []
                if not self.match(TK_RPAREN):
                    while True:
                        args.append(self.parse_expr())
                        if not self.match(TK_COMMA): break
                        self.consume(TK_COMMA)
                self.consume(TK_RPAREN); return Call(name, args)
            return Ident(name)
        if t == TK_LPAREN:
            self.consume(TK_LPAREN); expr = self.parse_expr(); self.consume(TK_RPAREN)
            return expr
        raise SyntaxError(f"Line {self.peek()[2]}: unexpected token {t!r}")


# ---------------------------------------------------------------------------
# Frame layout pre-pass
# ---------------------------------------------------------------------------

def count_locals(node) -> int:
    """Count the maximum number of 4-byte locals reachable in a function body."""
    if isinstance(node, Block):
        return sum(count_locals(s) for s in node.stmts)
    if isinstance(node, VarDecl):
        return 1
    if isinstance(node, IfStmt):
        e = count_locals(node.then_) + (count_locals(node.else_) if node.else_ else 0)
        return e
    if isinstance(node, (WhileStmt,)):
        return count_locals(node.body)
    if isinstance(node, ForStmt):
        return (1 if isinstance(node.init, VarDecl) else 0) + count_locals(node.body)
    return 0


# ---------------------------------------------------------------------------
# Code generator
# ---------------------------------------------------------------------------

ALLOC_REGS = [f'R{i}' for i in range(4, 13)]   # R4-R12 for general use
ARG_REGS   = ['R0', 'R1', 'R2', 'R3']
RET_REG    = 'R0'
SP         = 'R14'
LR         = 'R13'


class CodeGen:
    def __init__(self):
        self.lines: List[str] = []
        self._label_count = 0
        self.globals: Dict[str, Optional[int]] = {}

        # Per-function state
        self._vars: Dict[str, int] = {}  # name -> byte offset from SP (0 = top of frame)
        self._frame_size = 0             # total frame bytes allocated this function
        self._reg_free: List[str] = []
        self._reg_used: List[str] = []

    def emit(self, line: str): self.lines.append(line)
    def label(self, name: str): self.lines.append(f'{name}:')

    def fresh_label(self, prefix='.L') -> str:
        self._label_count += 1
        return f'{prefix}{self._label_count}'

    def _alloc_reg(self) -> str:
        if not self._reg_free:
            raise RuntimeError("Register spill not yet implemented — too many live values")
        r = self._reg_free.pop(0); self._reg_used.append(r); return r

    def _free_reg(self, r: str):
        if r in self._reg_used:
            self._reg_used.remove(r); self._reg_free.insert(0, r)

    def _load_imm(self, reg: str, value: int):
        """Emit instruction(s) to load an integer constant into reg."""
        v = value & 0xFFFFFFFF  # treat as unsigned 32-bit
        sv = value if value >= -(1<<31) else value  # keep signed
        if 0 <= value <= 15:
            self.emit(f'    ORI {reg}, R0, {value}')
        elif -8 <= value <= 7:
            self.emit(f'    ADDI {reg}, R0, {value}')
        else:
            lo4  = value & 0xF
            hi12 = (value >> 4) & 0xFFF
            self.emit(f'    EXT #{hi12}')
            self.emit(f'    ORI {reg}, R0, {lo4}')

    def _load_global_addr(self, reg: str, name: str):
        self.emit(f'    EXT #{name}')
        self.emit(f'    ADDI {reg}, R15, #0   ; address of {name}')

    def _alloc_local(self, name: str) -> int:
        """Reserve a 4-byte slot in the frame and map name to it.
        Returns the SP-relative offset (from the fixed post-prologue SP)."""
        offset = self._frame_size  # 0-based from SP top-of-frame
        self._vars[name] = offset
        self._frame_size += 4
        return offset

    def _lookup_var(self, name: str) -> Tuple[str, Optional[int]]:
        if name in self._vars:
            return 'local', self._vars[name]
        if name in self.globals:
            return 'global', None
        raise NameError(f"Undefined variable: {name!r}")

    # ------------------------------------------------------------------ top

    def generate(self, prog: Program) -> str:
        for decl in prog.decls:
            if isinstance(decl, GlobalVar):
                self.globals[decl.name] = decl.init

        if self.globals:
            self.emit('.section .data')
            for name, init in self.globals.items():
                self.emit(f'{name}:')
                self.emit(f'    .word {init if init is not None else 0}')
            self.emit('')

        self.emit('.section .text')
        for decl in prog.decls:
            if isinstance(decl, FuncDef):
                self._gen_func(decl)

        return '\n'.join(self.lines) + '\n'

    # ------------------------------------------------------------------ func

    def _gen_func(self, func: FuncDef):
        # Reset per-function state
        self._vars = {}
        self._frame_size = 0
        self._reg_free = list(ALLOC_REGS)
        self._reg_used = []

        # Pre-allocate params (they'll be stored into the frame)
        for _, pname in func.params:
            self._alloc_local(pname)

        # Pre-allocate all locals via a pre-pass so we know total frame size
        self._pre_alloc_locals(func.body)

        # Align frame to 8 bytes
        frame = (self._frame_size + 7) & ~7
        # +4 for saved LR
        total = frame + 4

        self.emit(f'.global {func.name}')
        self.label(func.name)
        # Prologue: save LR and adjust SP
        self.emit(f'    PUSH R13              ; save link register')
        if frame > 0:
            self._emit_addi_sp(-frame)

        # Store argument registers into their frame slots
        for i, (_, pname) in enumerate(func.params):
            off = self._vars[pname]
            self.emit(f'    ST {ARG_REGS[i]}, [R14, #{off}]  ; param {pname}')

        end_label = self.fresh_label(f'.{func.name}_end')
        self._gen_block_stmts(func.body.stmts, end_label)

        self.label(end_label)
        # Epilogue
        if frame > 0:
            self._emit_addi_sp(frame)
        self.emit(f'    POP R13               ; restore link register')
        self.emit(f'    RET')
        self.emit('')

    def _emit_addi_sp(self, delta: int):
        """Emit an SP adjustment, using EXT for large deltas."""
        if -8 <= delta <= 7:
            self.emit(f'    ADDI R14, R14, #{delta}')
        else:
            lo4  = delta & 0xF
            hi12 = (delta >> 4) & 0xFFF
            self.emit(f'    EXT #{hi12}')
            self.emit(f'    ADDI R14, R14, #{lo4}')

    def _pre_alloc_locals(self, node):
        """Walk the AST pre-allocating stack slots for all VarDecls."""
        if isinstance(node, Block):
            for s in node.stmts: self._pre_alloc_locals(s)
        elif isinstance(node, VarDecl):
            if node.name not in self._vars:
                self._alloc_local(node.name)
        elif isinstance(node, IfStmt):
            self._pre_alloc_locals(node.then_)
            if node.else_: self._pre_alloc_locals(node.else_)
        elif isinstance(node, WhileStmt):
            self._pre_alloc_locals(node.body)
        elif isinstance(node, ForStmt):
            if node.init: self._pre_alloc_locals(node.init)
            self._pre_alloc_locals(node.body)

    # ---------------------------------------------------------------- stmts

    def _gen_block_stmts(self, stmts, end_label: str):
        for stmt in stmts:
            self._gen_stmt(stmt, end_label)

    def _gen_stmt(self, stmt, end_label: str):
        if isinstance(stmt, VarDecl):
            # Slot already allocated; just emit the initializer store if present
            if stmt.init is not None:
                r = self._gen_expr(stmt.init)
                off = self._vars[stmt.name]
                self.emit(f'    ST {r}, [R14, #{off}]  ; init {stmt.name}')
                self._free_reg(r)
        elif isinstance(stmt, ExprStmt):
            r = self._gen_expr(stmt.expr)
            if r: self._free_reg(r)
        elif isinstance(stmt, ReturnStmt):
            if stmt.expr is not None:
                r = self._gen_expr(stmt.expr)
                if r != RET_REG:
                    self.emit(f'    MOV {RET_REG}, {r}'); self._free_reg(r)
            self.emit(f'    JMP {end_label}')
        elif isinstance(stmt, IfStmt):
            self._gen_if(stmt, end_label)
        elif isinstance(stmt, WhileStmt):
            self._gen_while(stmt, end_label)
        elif isinstance(stmt, ForStmt):
            self._gen_for(stmt, end_label)
        elif isinstance(stmt, Block):
            self._gen_block_stmts(stmt.stmts, end_label)
        else:
            raise NotImplementedError(f"Unknown stmt: {type(stmt)}")

    def _gen_if(self, stmt: IfStmt, end_label: str):
        else_label = self.fresh_label()
        done_label = self.fresh_label() if stmt.else_ else else_label
        r = self._gen_expr(stmt.cond)
        self.emit(f'    CMPI {r}, R0, #0'); self._free_reg(r)
        self.emit(f'    B.EQ {else_label}')
        self._gen_stmt(stmt.then_, end_label)
        if stmt.else_:
            self.emit(f'    JMP {done_label}')
            self.label(else_label)
            self._gen_stmt(stmt.else_, end_label)
            self.label(done_label)
        else:
            self.label(else_label)

    def _gen_while(self, stmt: WhileStmt, end_label: str):
        cond_lbl = self.fresh_label(); done_lbl = self.fresh_label()
        self.label(cond_lbl)
        r = self._gen_expr(stmt.cond)
        self.emit(f'    CMPI {r}, R0, #0'); self._free_reg(r)
        self.emit(f'    B.EQ {done_lbl}')
        self._gen_stmt(stmt.body, end_label)
        self.emit(f'    JMP {cond_lbl}')
        self.label(done_lbl)

    def _gen_for(self, stmt: ForStmt, end_label: str):
        if stmt.init: self._gen_stmt(stmt.init, end_label)
        cond_lbl = self.fresh_label(); done_lbl = self.fresh_label()
        self.label(cond_lbl)
        r = self._gen_expr(stmt.cond)
        self.emit(f'    CMPI {r}, R0, #0'); self._free_reg(r)
        self.emit(f'    B.EQ {done_lbl}')
        self._gen_stmt(stmt.body, end_label)
        if stmt.step:
            r2 = self._gen_expr(stmt.step)
            if r2: self._free_reg(r2)
        self.emit(f'    JMP {cond_lbl}')
        self.label(done_lbl)

    # --------------------------------------------------------------- exprs

    def _gen_expr(self, expr) -> str:
        if isinstance(expr, Literal):
            r = self._alloc_reg(); self._load_imm(r, expr.value); return r

        if isinstance(expr, Ident):
            r = self._alloc_reg()
            kind, off = self._lookup_var(expr.name)
            if kind == 'local':
                self.emit(f'    LD {r}, [R14, #{off}]  ; {expr.name}')
            else:
                addr = self._alloc_reg()
                self._load_global_addr(addr, expr.name)
                self.emit(f'    LD {r}, [{addr}, #0]  ; global {expr.name}')
                self._free_reg(addr)
            return r

        if isinstance(expr, Assign):
            rval = self._gen_assign_rhs(expr)
            self._gen_store(expr.target, rval)
            return rval

        if isinstance(expr, BinOp):
            return self._gen_binop(expr)

        if isinstance(expr, UnaryOp):
            return self._gen_unary(expr)

        if isinstance(expr, Call):
            return self._gen_call(expr)

        raise NotImplementedError(f"Unknown expr: {type(expr)}")

    def _gen_assign_rhs(self, assign: Assign) -> str:
        if assign.op == TK_ASSIGN:
            return self._gen_expr(assign.value)
        lval = self._gen_expr(assign.target)
        rhs  = self._gen_expr(assign.value)
        OP_MAP = {TK_PLUSEQ:'ADD', TK_MINUSEQ:'SUB', TK_STAREQ:'MUL',
                  TK_SLASHEQ:'DIV', TK_AMPEQ:'AND', TK_PIPEEQ:'OR',
                  TK_CARETEQ:'XOR', TK_LSHIFTEQ:'LSL', TK_RSHIFTEQ:'ASR'}
        if assign.op == TK_PERCENTEQ:
            qt = self._alloc_reg()
            self.emit(f'    DIV {qt}, {lval}, {rhs}')
            self.emit(f'    MUL {qt}, {qt}, {rhs}')
            self.emit(f'    SUB {lval}, {lval}, {qt}')
            self._free_reg(qt); self._free_reg(rhs); return lval
        instr = OP_MAP.get(assign.op)
        if instr:
            self.emit(f'    {instr} {lval}, {lval}, {rhs}')
            self._free_reg(rhs); return lval
        raise NotImplementedError(f"Compound assignment {assign.op!r}")

    def _gen_store(self, target, r_val: str):
        if isinstance(target, Ident):
            kind, off = self._lookup_var(target.name)
            if kind == 'local':
                self.emit(f'    ST {r_val}, [R14, #{off}]  ; {target.name}')
            else:
                addr = self._alloc_reg()
                self._load_global_addr(addr, target.name)
                self.emit(f'    ST {r_val}, [{addr}, #0]  ; global {target.name}')
                self._free_reg(addr)
        else:
            raise NotImplementedError("Only simple variable assignment supported")

    def _gen_binop(self, expr: BinOp) -> str:
        if expr.op == TK_AND: return self._gen_logical_and(expr)
        if expr.op == TK_OR:  return self._gen_logical_or(expr)

        left  = self._gen_expr(expr.left)
        right = self._gen_expr(expr.right)
        rd = left

        OP = {TK_PLUS:'ADD', TK_MINUS:'SUB', TK_STAR:'MUL', TK_SLASH:'DIV',
              TK_AMP:'AND', TK_PIPE:'OR', TK_CARET:'XOR',
              TK_LSHIFT:'LSL', TK_RSHIFT:'ASR'}
        CMP_OPS = {TK_EQ, TK_NEQ, TK_LT, TK_LE, TK_GT, TK_GE}

        if expr.op == TK_PERCENT:
            qt = self._alloc_reg()
            self.emit(f'    DIV {qt}, {left}, {right}')
            self.emit(f'    MUL {qt}, {qt}, {right}')
            self.emit(f'    SUB {rd}, {left}, {qt}')
            self._free_reg(qt); self._free_reg(right); return rd

        if expr.op in OP:
            self.emit(f'    {OP[expr.op]} {rd}, {left}, {right}')
            self._free_reg(right); return rd

        if expr.op in CMP_OPS:
            self.emit(f'    CMP {left}, {right}'); self._free_reg(right)
            skip = self.fresh_label()
            self.emit(f'    ORI {rd}, R0, #1')
            if expr.op == TK_LE:
                s2 = self.fresh_label()
                self.emit(f'    B.EQ {s2}'); self.emit(f'    B.LT {s2}')
                self.emit(f'    ORI {rd}, R0, #0')
                self.emit(f'    JMP {skip}')
                self.label(s2); self.label(skip)
            elif expr.op == TK_GT:
                s2 = self.fresh_label()
                self.emit(f'    B.EQ {skip}')
                self.emit(f'    B.GE {s2}')
                self.emit(f'    ORI {rd}, R0, #0'); self.emit(f'    JMP {skip}')
                self.label(s2); self.label(skip)
            else:
                BR = {TK_EQ:'B.EQ', TK_NEQ:'B.NE', TK_LT:'B.LT', TK_GE:'B.GE',
                      TK_LTU:'B.LTU', TK_GEU:'B.GEU'} if False else \
                     {TK_EQ:'B.EQ', TK_NEQ:'B.NE', TK_LT:'B.LT', TK_GE:'B.GE'}
                self.emit(f'    {BR[expr.op]} {skip}')
                self.emit(f'    ORI {rd}, R0, #0')
                self.label(skip)
            return rd

        raise NotImplementedError(f"BinOp {expr.op!r}")

    def _gen_logical_and(self, expr: BinOp) -> str:
        false_lbl = self.fresh_label(); done_lbl = self.fresh_label()
        rd = self._alloc_reg()
        left = self._gen_expr(expr.left)
        self.emit(f'    CMPI {left}, R0, #0'); self._free_reg(left)
        self.emit(f'    B.EQ {false_lbl}')
        right = self._gen_expr(expr.right)
        self.emit(f'    CMPI {right}, R0, #0'); self._free_reg(right)
        self.emit(f'    B.EQ {false_lbl}')
        self.emit(f'    ORI {rd}, R0, #1')
        self.emit(f'    JMP {done_lbl}')
        self.label(false_lbl); self.emit(f'    ORI {rd}, R0, #0')
        self.label(done_lbl); return rd

    def _gen_logical_or(self, expr: BinOp) -> str:
        true_lbl = self.fresh_label(); done_lbl = self.fresh_label()
        rd = self._alloc_reg()
        left = self._gen_expr(expr.left)
        self.emit(f'    CMPI {left}, R0, #0'); self._free_reg(left)
        self.emit(f'    B.NE {true_lbl}')
        right = self._gen_expr(expr.right)
        self.emit(f'    CMPI {right}, R0, #0'); self._free_reg(right)
        self.emit(f'    B.NE {true_lbl}')
        self.emit(f'    ORI {rd}, R0, #0')
        self.emit(f'    JMP {done_lbl}')
        self.label(true_lbl); self.emit(f'    ORI {rd}, R0, #1')
        self.label(done_lbl); return rd

    def _gen_unary(self, expr: UnaryOp) -> str:
        if expr.op == '-':
            r = self._gen_expr(expr.operand)
            zero = self._alloc_reg()
            self.emit(f'    ORI {zero}, R0, #0')
            self.emit(f'    SUB {r}, {zero}, {r}'); self._free_reg(zero); return r
        if expr.op == '~':
            r = self._gen_expr(expr.operand)
            ones = self._alloc_reg()
            self.emit(f'    ADDI {ones}, R0, #-1')
            self.emit(f'    XOR {r}, {r}, {ones}'); self._free_reg(ones); return r
        if expr.op == '!':
            r = self._gen_expr(expr.operand)
            skip = self.fresh_label()
            self.emit(f'    CMPI {r}, R0, #0')
            self.emit(f'    ORI {r}, R0, #0')
            self.emit(f'    B.NE {skip}')
            self.emit(f'    ORI {r}, R0, #1')
            self.label(skip); return r
        if expr.op in ('++', '--'):
            instr = 'ADDI' if expr.op == '++' else 'SUBI'
            if expr.post:
                old = self._alloc_reg()
                r = self._gen_expr(expr.operand)
                self.emit(f'    MOV {old}, {r}')
                self.emit(f'    {instr} {r}, {r}, #1')
                self._gen_store(expr.operand, r); self._free_reg(r); return old
            else:
                r = self._gen_expr(expr.operand)
                self.emit(f'    {instr} {r}, {r}, #1')
                self._gen_store(expr.operand, r); return r
        raise NotImplementedError(f"Unary {expr.op!r}")

    def _gen_call(self, expr: Call) -> str:
        if len(expr.args) > 4:
            raise NotImplementedError("More than 4 arguments not supported")
        arg_tmps = [self._gen_expr(a) for a in expr.args]
        for i, (tmp, areg) in enumerate(zip(arg_tmps, ARG_REGS)):
            if tmp != areg:
                self.emit(f'    MOV {areg}, {tmp}')
            self._free_reg(tmp)
        self.emit(f'    CALL {expr.name}')
        rd = self._alloc_reg()
        if rd != RET_REG:
            self.emit(f'    MOV {rd}, {RET_REG}')
        return rd


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def compile_c(src: str) -> str:
    tokens = lex(src)
    ast = Parser(tokens).parse_program()
    return CodeGen().generate(ast)


def main():
    ap = argparse.ArgumentParser(
        description='Aurora C Compiler — compiles C subset to Aurora v1.2 assembly')
    ap.add_argument('input', help='Input C source file')
    ap.add_argument('-o', '--output', help='Output assembly file (default: stdout)')
    args = ap.parse_args()
    with open(args.input) as f:
        src = f.read()
    asm = compile_c(src)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(asm)
        print(f'Wrote {args.output}')
    else:
        print(asm)

if __name__ == '__main__':
    main()
