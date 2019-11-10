from colorama import Fore, Style
from dataclasses import dataclass
from typing import List, Dict, Any, Union, Tuple, Sequence

from pox.token_types import NUMBER, PLUS, OPEN_PAREN, CLOSE_PAREN, STAR, FUN, IDENTIFIER, COMMA, OPEN_BRACE, CLOSE_BRACE, PRINT, SEMICOLON, TokenType, RETURN
from pox.tokenizer import Token, Tuple, TypeVar, Generic, Callable
from operator import add, mul

T = TypeVar('T')


class Src:
    src = ''


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
class Identifier(AST):
    symbol: str


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
    parameters: Sequence[str]
    body: Block


@dataclass(frozen=True)
class FunctionApply(AST):
    f_name: str
    arg_names: Tuple[str]


@dataclass(frozen=True)
class Print(AST):
    expr: 'Expr'


# how is this different from a literal?
@dataclass(frozen=True)
class Value(AST, Generic[T]):
    val: T




Expr = Union[Binary, Literal, Grouping, Function, FunctionApply, Identifier]
Statement = Union[FunctionApply, Print]  # Var, Function

@dataclass(frozen=True)
class Return(AST):
    expr: Expr


def check(tokens: Sequence[Token], i: int, n: int, expected: Sequence[TokenType]) -> None:
    for j in range(n):
        k = i + j
        if k > len(tokens):
            raise RuntimeError(f"Out of bounds! i: {i}, j: {j} -- ")

        token = tokens[k]

        if token.token_type is not expected[j]:
            msg = f"Expected {expected[j]}\nCharacter: {token.char}"
            panic(tokens, k, msg)


def panic(tokens: Sequence[Token], i: int, msg: str) -> None:
    src = Src.src
    color = Fore.LIGHTRED_EX
    try:
        token = tokens[i]
        start = token.char
        end = token.char + len(token.lexeme)
        print(src[:start], end='')
        err = src[start:end]
        print(f"{color}{err}{Style.RESET_ALL}", end='')
        print(src[end:])
    except Exception:
        raise
    msg += f'\n{color}Look for this above{Style.RESET_ALL}'
    raise RuntimeError(msg)


def _stmt(tokens: Sequence[Token], i: int) -> Tuple[Any, int]:
    if tokens[i].token_type is PRINT:
        stmt, j = _print(tokens, i)
        assert tokens[j].token_type is SEMICOLON, (j, tokens[j])
    elif tokens[i].token_type is FUN:
        stmt, j = _function(tokens, i)
        # assert tokens[j].token_type is SEMICOLON, (j, tokens[j])
    elif tokens[i].token_type is RETURN:
        stmt, j = _return(tokens, i)
        return stmt, j
    else:
        stmt, j = _expression(tokens, i)
        assert tokens[j].token_type is SEMICOLON, (j, tokens[j])
    return stmt, j + 1


def _return(tokens: Sequence[Token], i: int) -> Tuple[Return, int]:
    assert tokens[i].token_type is RETURN
    expr, j = _expression(tokens, i + 1)
    assert tokens[j].token_type is SEMICOLON
    return Return(expr), j + 1


def _program(tokens: Sequence[Token], i: int) -> Tuple[Program, int]:
    statements: List[Statement] = []
    j = i
    while j < len(tokens):
        stmt, k = _stmt(tokens, j)
        statements.append(stmt)
        j = k
    program = Program(tuple(statements))
    return program, j


def _print(tokens: Sequence[Token], i: int) -> Tuple[Print, int]:
    check(tokens, i, 2, (PRINT, OPEN_PAREN,))
    expr, j = _expression(tokens, i + 2)
    check(tokens, j, 1, (CLOSE_PAREN,))
    return Print(expr), j + 1


def _expression(tokens: Sequence[Token], i: int) -> Tuple[Expr, int]:
    return _addition(tokens, i)


def _addition(tokens: Sequence[Token], i: int) -> Tuple[Expr, int]:
    expr, j = _multiplication(tokens, i)

    while j < len(tokens) and tokens[j].token_type is PLUS:
        operator = tokens[j] # todo ...
        right, j = _multiplication(tokens, j + 1)
        expr = Binary(add, left=expr, right=right)

    return expr, j


def _multiplication(tokens: Sequence[Token], i: int) -> Tuple[Expr, int]:
    expr, j = _primary(tokens, i)

    while j < len(tokens) and tokens[j].token_type is STAR:
        operator = tokens[j] # todo ...
        right, j = _primary(tokens, j + 1)
        expr = Binary(mul, left=expr, right=right)

    return expr, j


def _primary(tokens: Sequence[Token], i: int) -> Tuple[Expr, int]:
    token = tokens[i]

    if token.token_type is NUMBER:
        return Literal(float(token.lexeme)), i + 1

    if token.token_type is IDENTIFIER:
        return Identifier(symbol=token.lexeme), i + 1

    if token.token_type is OPEN_PAREN:
        expr, j = _expression(tokens, i + 1)
        assert tokens[j].token_type is CLOSE_PAREN
        return Grouping(expr), j + 1

    panic(tokens, i, msg="Fell off the end of _primary")


def types(ts: Sequence[Token]):
    return tuple(t.token_type for t in ts)


def _block(tokens: Sequence[Token], i: int) -> Tuple[Block, int]:
    assert tokens[i].token_type is OPEN_BRACE
    j = i + 1
    statements: List[Statement] = []
    while j < len(tokens) and tokens[j].token_type is not CLOSE_BRACE:
        stmt, k = _stmt(tokens, j)
        statements.append(stmt)
        j = k
    assert tokens[j].token_type is CLOSE_BRACE
    return Block(tuple(statements)), j + 1


def _function(tokens: Sequence[Token], i: int) -> Tuple[AST, int]:
    assert types(tokens[i:i+3]) == (FUN, IDENTIFIER, OPEN_PAREN)

    name = tokens[1].lexeme

    j = i + 3
    parameters = []

    while j < len(tokens) and tokens[j].token_type is not CLOSE_PAREN:
        assert tokens[j].token_type is IDENTIFIER
        parameters.append(tokens[j].lexeme)
        assert tokens[j + 1].token_type in (COMMA, CLOSE_PAREN)
        if tokens[j + 1].token_type is COMMA:
            j += 2
        else:
            j += 1
    assert j < len(tokens)
    assert tokens[j].token_type is CLOSE_PAREN
    block, k = _block(tokens, j + 1)

    if k < len(tokens) and tokens[k].token_type is SEMICOLON:
        k += 1

    return Function(name=name, parameters=parameters, body=block), k


def _parse(tokens: Sequence[Token]) -> AST:
    ast, _ = _program(tokens, 0)
    return ast


def lex_and_parse(src: str) -> AST:
    from pox.tokenizer import tokenize
    Src.src = src
    tokens = tokenize(src)
    ast = _parse(tokens)
    return ast


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

    if isinstance(ast, Return):
        return {
            "type": "return",
            "expr": to_json(ast.expr),
        }

    if isinstance(ast, Function):
        return {
            "type": "function",
            "name": ast.name,
            "parameters": ast.parameters,
            "body": [to_json(x) for x in ast.body.statements],
        }

    if isinstance(ast, Identifier):
        return {
            "type": "identifier",
            "symbol": ast.symbol,
        }

    assert False, repr(ast)
