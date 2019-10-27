from dataclasses import dataclass
from typing import List, Dict, Any

from pox.token_types import NUMBER, PLUS, OPEN_PAREN, CLOSE_PAREN, STAR
from pox.tokenizer import Token, Tuple, TypeVar, Generic, Callable
from operator import add, mul

T = TypeVar('T')


@dataclass(frozen=True)
class AST:
    pass


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


def _expression(tokens: List[Token], i: int) -> Tuple[AST, int]:
    return _addition(tokens, i)


def _multiplication(tokens: List[Token], i: int) -> Tuple[AST, int]:
    expr, j = _primary(tokens, i)

    while j < len(tokens) and tokens[j].token_type is STAR:
        operator = tokens[j] # todo ...
        right, j = _primary(tokens, j + 1)
        expr = Binary(mul, left=expr, right=right)

    return expr, j


def _addition(tokens: List[Token], i: int) -> Tuple[AST, int]:
    expr, j = _multiplication(tokens, i)

    while j < len(tokens) and tokens[j].token_type is PLUS:
        operator = tokens[j] # todo ...
        right, j = _multiplication(tokens, j + 1)
        expr = Binary(add, left=expr, right=right)

    return expr, j


def _primary(tokens: List[Token], i: int) -> Tuple[AST, int]:
    token = tokens[i]

    if token.token_type is NUMBER:
        return Literal(float(token.lexeme)), i + 1

    if token.token_type is OPEN_PAREN:
        expr, j = _expression(tokens, i + 1)
        assert tokens[j].token_type is CLOSE_PAREN
        return Grouping(expr), j + 1


def _parse(tokens: List[Token], i: int) -> Tuple[AST, int]:
    return _expression(tokens, i)


def parse(tokens: List[Token]) -> AST:
    ast, _ = _parse(tokens, 0)
    return ast

from pox.tokenizer import tokenize

src = '1 + 2 + (3 + 4) * 5'
ts = tokenize(src)
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

    assert False, repr(ast)


js = to_json(ast)

import json

print(json.dumps(js, indent=4))
