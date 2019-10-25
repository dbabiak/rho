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


__all__ = ["tokenize"]

def main():
    some_javascript = """
    "use strict";
    function _slicedToArray(e, t) {
        return _arrayWithHoles(e) || _iterableToArrayLimit(e, t) || _nonIterableRest()
    }
    function _nonIterableRest() {
        throw new TypeError("Invalid attempt to destructure non-iterable instance")
    }
    function _iterableToArrayLimit(e, t) {
        var n = []
          , i = !0
          , a = !1
          , s = void 0;
        try {
            for (var o, r = e[Symbol.iterator](); !(i = (o = r.next()).done) && (n.push(o.value),
            !t || n.length !== t); i = !0)
                ;
        } catch (e) {
            a = !0,
            s = e
        } finally {
            try {
                i || null == r.return || r.return()
            } finally {
                if (a)
                    throw s
            }
        }
        return n
    }
    function _arrayWithHoles(e) {
        if (Array.isArray(e))
            return e
    }
    self.window = self,
    self.importScripts("/public/ace/1.4.3/ace.js");
    var _require = window.ace.require
      , Tokenizer = _require("ace/tokenizer").Tokenizer
      , documents = {};
    self.addEventListener("message", function(e) {
        var t = e.data
          , n = t.code
          , i = t.visibleRange
          , a = t.mode
          , s = t.changeStartRow
          , o = t.documentId
          , r = _slicedToArray(i, 2)
          , l = r[0]
          , c = r[1]
          , u = getTokenizer(a)
          , d = n.split("\n")
          , m = [];
        documents[o] || (documents[o] = {
            classifications: [],
            states: [],
            lastValidRow: 0,
            cleanTimeout: null
        }),
        null != s && (documents[o].lastValidRow = Math.min(documents[o].lastValidRow, s),
        documents[o].classifications = documents[o].classifications.slice(0, documents[o].lastValidRow),
        documents[o].states = documents[o].states.slice(0, documents[o].lastValidRow)),
        clearTimeout(documents[o].cleanTimeout);
        for (var f = Math.min(l, documents[o].lastValidRow); f <= Math.min(c, d.length - 1); f++)
            if (documents[o].classifications[f]) {
                if (f < l)
                    continue;
                m = m.concat(documents[o].classifications[f])
            } else {
                var y = u.getLineTokens(d[f], documents[o].states[f - 1] || "start", f)
                  , v = y.tokens
                  , h = y.state;
                documents[o].states[f] = h,
                documents[o].lastValidRow = Math.max(f, documents[o].lastValidRow);
                var w = 1
                  , g = []
                  , R = !0
                  , T = !1
                  , p = void 0;
                try {
                    for (var k, b = v[Symbol.iterator](); !(R = (k = b.next()).done); R = !0) {
                        var _ = k.value;
                        if ("text" !== _.type && "identifier" !== _.type) {
                            var z = _.type.split(".")
                              , V = !0
                              , M = !1
                              , A = void 0;
                            try {
                                for (var L, S = z[Symbol.iterator](); !(V = (L = S.next()).done); V = !0) {
                                    var x = L.value;
                                    g.push({
                                        startLine: f + 1,
                                        endLine: f + 1,
                                        kind: x,
                                        start: w,
                                        end: w + _.value.length
                                    })
                                }
                            } catch (e) {
                                M = !0,
                                A = e
                            } finally {
                                try {
                                    V || null == S.return || S.return()
                                } finally {
                                    if (M)
                                        throw A
                                }
                            }
                            w += _.value.length
                        } else
                            w += _.value.length
                    }
                } catch (e) {
                    T = !0,
                    p = e
                } finally {
                    try {
                        R || null == b.return || b.return()
                    } finally {
                        if (T)
                            throw p
                    }
                }
                m = m.concat(g),
                documents[o].classifications[f] = g
            }
        self.postMessage({
            classifications: m
        }),
        documents[o].cleanTimeout = setTimeout(function() {
            documents[o] = {
                classifications: [],
                states: [],
                lastValidRow: 0,
                cleanTimeout: null
            }
        }, 6e4)
    });
    var tokenizers = {};
    function getTokenizer(e) {
        if (null == tokenizers[e]) {
            var t = getModeRules(e);
            tokenizers[e] = new Tokenizer(t)
        }
        return tokenizers[e]
    }
    function getModeRules(e) {
        return self.importScripts("/public/ace/1.4.3/mode-".concat(e, ".js")),
        (new ((new (_require("ace/mode/".concat(e)).Mode)).HighlightRules)).getRules()
    }
    """
    tokens = tokenize(some_javascript)
    for i, t in enumerate(tokens):
        print(f"{t.lexeme:20} {t.token_type.name:20}")


if __name__ == '__main__':
    main()
