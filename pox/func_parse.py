from dataclasses import dataclass
from typing import List, Dict, Any, Union, Tuple, Sequence

from pox.token_types import NUMBER, PLUS, OPEN_PAREN, CLOSE_PAREN, STAR, FUN, IDENTIFIER, COMMA, OPEN_BRACE, CLOSE_BRACE, PRINT, SEMICOLON, TokenType
from pox.tokenizer import Token, Tuple, TypeVar, Generic, Callable
from operator import add, mul

T = TypeVar('T')


# why even have an AST class at this point?
@dataclass(frozen=True)
class AST:
    pass


@dataclass(frozen=True)
class Block(AST):
    statements: Tuple['Statement']


# why have something other than a block if they are isomorphic?
@dataclass(frozen=True)
class Program(AST):
    statements: Tuple['Statement']


@dataclass(frozen=True)
class Binary(AST):
    operator: Callable[[float, float], float]
    left: AST
    right: AST


@dataclass(frozen=True)
class Literal(AST, Generic[T]):
    val: T


@dataclass(frozen=True)
class Grouping(AST):
    expr: AST


@dataclass(frozen=True)
class Var(AST):
    symbol: str
    referent: 'Expr'  # wrong! this should be an expression!


@dataclass(frozen=True)
class Function(AST):
    name: str
    parameters: List[str]
    body: Block


@dataclass(frozen=True)
class FunctionApply(AST):
    f_name: str
    arg_names: Tuple[str]


@dataclass(frozen=True)
class Print(AST):
    expr: 'Expr'


Expr = Union[Binary, Literal, Grouping, Function, FunctionApply]
Statement = Union[FunctionApply, Print]  # Var, Function


def check(tokens: Tuple[Token], i: int, n: int, expected: Sequence[TokenType]) -> None:
    for j in range(n):
        k = i + j
        if k > len(tokens):
            raise RuntimeError(f"Out of bounds! i: {i}, j: {j} -- ")

        token = tokens[k]

        if token.token_type is not expected[j]:
            try:
                marked = src[:k] + '@' + src[k + 1:]
                print(marked)
            except Exception:
                pass
            raise RuntimeError(f"""
Assert failed! 

Expected {expected[k]}
Character: {token.char}
Look for @ above
            """)


def _program(tokens: Tuple[Token], i: int) -> Tuple[Program, int]:
    statements: List[Statement] = []
    j = i
    while j < len(tokens):
        if tokens[j].token_type is PRINT:
            stmt, k = _print(tokens, j)
        else:
            stmt, k = _expression(tokens, j)
        assert tokens[k].token_type is SEMICOLON
        statements.append(stmt)
        j = k + 1

    program = Program(tuple(statements))
    return program, j


def _print(tokens: Tuple[Token], i: int) -> Tuple[Print, int]:
    check(tokens, i, 2, (PRINT, OPEN_PAREN,))
    expr, j = _expression(tokens, i + 2)
    assert tokens[j].token_type is CLOSE_PAREN
    return Print(expr), j + 1


def _expression(tokens: Tuple[Token], i: int) -> Tuple[Expr, int]:
    return _addition(tokens, i)


def _addition(tokens: Tuple[Token], i: int) -> Tuple[Expr, int]:
    expr, j = _multiplication(tokens, i)

    while j < len(tokens) and tokens[j].token_type is PLUS:
        operator = tokens[j] # todo ...
        right, j = _multiplication(tokens, j + 1)
        expr = Binary(add, left=expr, right=right)

    return expr, j


def _multiplication(tokens: Tuple[Token], i: int) -> Tuple[Expr, int]:
    expr, j = _primary(tokens, i)

    while j < len(tokens) and tokens[j].token_type is STAR:
        operator = tokens[j] # todo ...
        right, j = _primary(tokens, j + 1)
        expr = Binary(mul, left=expr, right=right)

    return expr, j


def _primary(tokens: Tuple[Token], i: int) -> Tuple[Expr, int]:
    token = tokens[i]

    if token.token_type is NUMBER:
        return Literal(float(token.lexeme)), i + 1

    if token.token_type is OPEN_PAREN:
        expr, j = _expression(tokens, i + 1)
        assert tokens[j].token_type is CLOSE_PAREN
        return Grouping(expr), j + 1


def types(ts: Tuple[Token]):
    return tuple(t.token_type for t in ts)


def _block(tokens: Tuple[Token], i: int) -> Tuple[Block, int]:
    assert tokens[i].token_type is OPEN_BRACE
    statements = []


def _function(tokens: Tuple[Token], i: int) -> Tuple[AST, int]:
    assert types(tokens[i:i+2]) == (FUN, OPEN_PAREN)

    parameters = []
    j = i + 2

    while j < len(tokens) and tokens[j].token_type is not CLOSE_PAREN:
        assert tokens[j].token_type is IDENTIFIER
        parameters.append(tokens[j].lexeme)
        assert tokens[j + 1].token_type in (COMMA, CLOSE_PAREN)
        if tokens[j + 1].token_type is COMMA:
            j += 2
    assert j < len(tokens)
    assert tokens[j].token_type is CLOSE_PAREN
    block = _block(tokens, j + 1)


def parse(tokens: Tuple[Token]) -> AST:
    ast, _ = _program(tokens, 0)
    return ast

from pox.tokenizer import tokenize
from pprint import pprint

src = '''
print(1);
print(2);
print(42 + 7 * 3);
'''
ts = tokenize(src)
pprint(dict(enumerate(types(ts))))
ast = parse(ts)


def to_json(ast: AST) -> Dict[str, Any]:
    if isinstance(ast, Binary):
        return {
            "type": "binary",
            "op": str(ast.operator),
            "left": to_json(ast.left),
            "right": to_json(ast.right),
        }

    if isinstance(ast, Literal):
        return {
            "type": "literal",
            "val": ast.val,
        }

    if isinstance(ast, Grouping):
        return {
            "type": "grouping",
            "expr": to_json(ast.expr),
        }

    if isinstance(ast, Print):
        return {
            "type": "print",
            "expr": to_json(ast.expr),
        }

    if isinstance(ast, Block):
        return {
            "type": "block",
            "statement": [
                to_json(x) for x in ast.statements
            ]
        }

    if isinstance(ast, Program):
        return {
            "type": "program",
            "statement": [
                to_json(x) for x in ast.statements
            ]
        }

    assert False, repr(ast)


js = to_json(ast)

import json

print(json.dumps(js, indent=4))
