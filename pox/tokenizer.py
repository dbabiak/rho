from dataclasses import dataclass
from enum import Enum, auto
from string import ascii_letters, digits
from typing import *

from pox.token_types import *

def peek(src: str, i: int) -> Optional[str]:
    if i < len(src):
        return src[i]

@dataclass
class Token:
    token_type: TokenType
    char: int
    lexeme: str

    def __repr__(self):
        return f"{self.token_type.name}(char={self.char}, lexeme={self.lexeme})"


def _fixed_length(src: str, i: int) -> Optional[Token]:
    token_types = {
        "(": OPEN_PAREN,
        ")": CLOSE_PAREN,
        "{": OPEN_BRACE,
        "}": CLOSE_BRACE,
        "[": OPEN_BRACKET,
        "]": CLOSE_BRACKET,
        ":": COLON,
        "@": AT,
        ",": COMMA,
        ".": DOT,
        "?": QUESTION,
        ";": SEMICOLON,
        "-": MINUS,
        "+": PLUS,
        "/": SLASH,
        "*": STAR,

        # the more restrictive has to come first!!
        "!=": BANG_EQUAL,
        "!": BANG,

        # the more restrictive has to come first!!
        "==": EQUAL_EQUAL,
        "=": EQUAL,

        # the more restrictive has to come first!!
        ">=": GREATER_EQUAL,
        ">": GREATER,

        # the more restrictive has to come first!!
        "<=": LESS_EQUAL,
        "<": LESS,

        "and": AND,
        # the more restrictive has to come first!!
        "&&": AND,
        "&": BINAND,

        "class": CLASS,
        "else": ELSE,
        "false": FALSE,
        "fun": FUN,
        "for": FOR,
        "if": IF,
        "null": NULL,

        "or": OR,
        # the more restrictive has to come first!!
        "||": OR,
        "|": BINOR,

        "^": XOR,
        "print": PRINT,
        "return": RETURN,
        "super": SUPER,
        "this": THIS,
        "true": TRUE,
        "var": VAR,
        "while": WHILE,
    }
    for lexeme, token_type in token_types.items():
        if src[i:i + len(lexeme)] == lexeme:
            return Token(token_type=token_type, char=i, lexeme=lexeme)


def _number(src: str, i: int) -> Optional[Token]:
    if src[i].isdigit():
        j = i + 1
        while j < len(src) and src[j].isdigit():
            j += 1

        # do we have a decimal? if yes, keep counting
        if j < len(src) and src[j] == ".":
            j += 1
            while j < len(src) and src[j].isdigit():
                j += 1

        return Token(token_type=NUMBER, char=i, lexeme=src[i:j])


def _string(src: str, i: int) -> Optional[Token]:
    if src[i] in ('\'', '\"'):
        quote = src[i]

        j = i + 1
        while j < len(src):
            if src[j] == quote:
                return Token(token_type=STRING, char=i, lexeme=src[i : j + 1])
            if src[j] == "\\":
                j += 2
            else:
                j += 1


def _identifier(src: str, i: int) -> Optional[Token]:
    if src[i] in ("_" + ascii_letters):
        j = i + 1
        while j < len(src) and src[j] in ("_" + ascii_letters + digits):
            j += 1
        return Token(token_type=IDENTIFIER, char=i, lexeme=src[i : j])


def _whitespace(src: str, i: int) -> Optional[Token]:
    if src[i].isspace():
        j = i + 1
        while j < len(src) and src[j].isspace():
            j += 1
        return Token(token_type=WHITESPACE, char=i, lexeme=src[i:j])


def _line_comment(src: str, i: int) -> Optional[Token]:
    if src[i:i+2] == '//':
        j = i + 1
        while j < len(src) and src[j] != '\n':
            if src[j] == '\\':
                j += 2
            else:
                j += 1
        return Token(token_type=LINE_COMMENT, char=i, lexeme=src[i:j + 1])


def _multi_line_comment(src: str, i: int) -> Optional[Token]:
    if src[i:i+2] == '/*':
        depth = 1
        j = i + 1
        while depth > 0 and j < len(src):
            if src[j] == '\\':
                j += 2
            elif src[j:j+2] == '/*':
                depth += 1
                j += 2
            elif src[j:j+2] == '*/':
                depth -= 1
                j += 2
            else:
                j += 1
        return Token(token_type=MULTI_LINE_COMMENT, char=i, lexeme=src[i:j])


_tokenizers: Sequence[Callable[[str, int], Optional[Token]]] = (
    _line_comment,
    _multi_line_comment,
    _fixed_length,
    _number,
    _string,
    _identifier,
    _whitespace,
)


def _next_token(src: str, i: int) -> Optional[Token]:
    for f in _tokenizers:
        token: Optional[Token] = f(src, i)
        if token:
            return token


class LexError(RuntimeError):
    pass


def tokenize(src: str) -> List[Token]:
    i = 0
    tokens = []

    while i < len(src):
        token = _next_token(src, i)
        if token is None:
            raise LexError(f"wat? failed to parse at char {i}")
        tokens.append(token)
        i += len(token.lexeme)

    return [t for t in tokens if t.token_type is not WHITESPACE ]


__all__ = ["tokenize", "Token"]
