from dataclasses import dataclass
from string import digits
from typing import *


class LexError(RuntimeError):
    pass


@dataclass
class Token:
    kind: str
    char: int
    lexeme: str

    def __repr__(self):
        return f"{self.kind.upper()}(char={self.char}, lexeme={self.lexeme})"


def _null(src: str, i: int) -> Optional[Token]:
    literal = "null"
    if src[i : i + len(literal)] == literal:
        return Token(kind="null", char=i, lexeme=literal)


def _true(src: str, i: int) -> Optional[Token]:
    literal = "true"
    if src[i : i + len(literal)] == literal:
        return Token(kind="true", char=i, lexeme=literal)


def _false(src: str, i: int) -> Optional[Token]:
    literal = "false"
    if src[i : i + len(literal)] == literal:
        return Token(kind="false", char=i, lexeme=literal)


def _number(src: str, i: int) -> Optional[Token]:
    if src[i] in digits:
        j = i + 1
        while j < len(src) and src[j] in digits:
            j += 1

        # do we have a decimal? if yes, keep counting
        if j < len(src) and src[j] == ".":
            j += 1
            while j < len(src) and src[j] in digits:
                j += 1

        return Token(kind="number", char=i, lexeme=src[i:j])


def _string(src: str, i: int) -> Optional[Token]:
    if src[i] == '"':
        j = i + 1
        while j < len(src):
            if src[j] == '"':
                return Token(kind="string", char=i, lexeme=src[i : j + 1])
            if src[j] == "\\":
                j += 2
            else:
                j += 1


def _open_brace(src: str, i: int) -> Optional[Token]:
    literal = "{"
    if src[i] == literal:
        return Token(kind="open_brace", char=i, lexeme=literal)


def _close_brace(src: str, i: int) -> Optional[Token]:
    literal = "}"
    if src[i] == literal:
        return Token(kind="close_brace", char=i, lexeme=literal)


def _open_bracket(src: str, i: int) -> Optional[Token]:
    literal = "["
    if src[i] == literal:
        return Token(kind="open_bracket", char=i, lexeme=literal)


def _close_bracket(src: str, i: int) -> Optional[Token]:
    literal = "]"
    if src[i] == literal:
        return Token(kind="close_bracket", char=i, lexeme=literal)


def _colon(src: str, i: int) -> Optional[Token]:
    literal = ":"
    if src[i] == literal:
        return Token(kind="colon", char=i, lexeme=literal)


def _comma(src: str, i: int) -> Optional[Token]:
    literal = ","
    if src[i] == literal:
        return Token(kind="comma", char=i, lexeme=literal)


def _whitespace(src: str, i: int) -> Optional[Token]:
    if src[i].isspace():
        j = i + 1
        while j < len(src) and src[j].isspace():
            j += 1
        return Token(kind="whitespace", char=i, lexeme=src[i:j])


_tokenizers = (
    _null,
    _true,
    _false,
    _number,
    _string,
    _open_brace,
    _close_brace,
    _open_bracket,
    _close_bracket,
    _colon,
    _comma,
    _whitespace,
)


def next_token(src: str, i: int) -> Optional[Token]:
    for f in _tokenizers:
        token: Optional[Token] = f(src, i)
        if token:
            return token


def tokenize(src: str) -> List[Token]:
    i = 0
    tokens = []

    while i < len(src):
        token = next_token(src, i)
        if token is None:
            raise LexError(f"wat? failed to parse at char {i}")
        tokens.append(token)
        i += len(token.lexeme)

    return [t for t in tokens if t.kind != "whitespace"]


__all__ = ["tokenize"]
