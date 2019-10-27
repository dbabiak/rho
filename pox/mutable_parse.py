from dataclasses import dataclass
from typing import Generic, TypeVar, Set, List

from pox.tokenizer import Token
from pox import token_types as TT


class AST:
    pass


@dataclass
class Binary(AST):
    left: AST
    op: str
    right: AST


@dataclass
class Unary(AST):
    op: str
    right: AST


T = TypeVar('T')
@dataclass
class Literal(AST, Generic[T]):
    val: T

@dataclass
class Grouping(AST):
    expr: AST


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()

        while self.match({TT.BANG_EQUAL, TT.EQUAL_EQUAL}):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(left=expr, op=operator.lexeme, right=right)

        return expr


    def match(self, token_types: Set[TT.TokenType]) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TT.TokenType) -> bool:
        return (not self.is_at_end()) and (self.peek().token_type == token_type)

    def peek(self) -> Token:
        return self.tokens[self.current]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def comparison(self):
        expr = self.addition()
        while self.match({TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL}):
            operator = self.previous()
            right = self.addition()
            expr = Binary(expr, operator.lexeme, right)
        return expr

    def addition(self):
        expr = self.multiplication()
        while self.match({TT.MINUS, TT.PLUS}):
            operator = self.previous()
            right = self.multiplication()
            expr = Binary(expr, operator.lexeme, right)
        return expr

    def multiplication(self):
        expr = self.unary()
        while self.match({TT.SLASH, TT.STAR}):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator.lexeme, right)
        return expr

    def unary(self):
        if self.match({TT.BANG, TT.MINUS}):
            operator = self.previous()
            right = self.unary()
            return Unary(operator.lexeme, right)
        else:
            return self.primary()

    def primary(self):
        if self.match({TT.FALSE}): return Literal(TT.FALSE)
        if self.match({TT.TRUE}): return Literal(TT.TRUE)
        if self.match({TT.NULL}): return Literal(TT.NULL)
        if self.match({TT.NUMBER}): return Literal(float(self.previous().lexeme))
        if self.match({TT.STRING}): return Literal(self.previous().lexeme)
        if self.match({TT.OPEN_PAREN}):
            expr = self.expression()
            self.consume(TT.CLOSE_PAREN, "Expect ')' after expression")
            return Grouping(expr)

    def consume(self, token_type: TT.TokenType, msg: str):
        if not self.match({token_type}):
            raise RuntimeError(msg)

    def parse(self):
        return self.expression()


from pox.tokenizer import tokenize

src = "42 * (7 + 3)"

tokens = tokenize(src)

parser = Parser(tokens)

ast = parser.parse()

print(repr(ast))
