from typing import *

from rho_lex import Token


JSON = Any

JSON = Union[type(None), float, bool, str, List[JSON], Dict[str, JSON]]

KV = Tuple[str, Any]


def _null(tokens: List[Token], i: int) -> Tuple[type(None), int]:
    assert tokens[i].kind == "null", i
    return None, i + 1


def _string(tokens: List[Token], i: int) -> Tuple[str, int]:
    assert tokens[i].kind == "string", i
    return tokens[i].lexeme[1:-1], i + 1


def _number(tokens: List[Token], i: int) -> Tuple[float, int]:
    assert tokens[i].kind == "number", i
    return float(tokens[i].lexeme), i + 1


def _bool(tokens: List[Token], i: int) -> Tuple[bool, int]:
    assert tokens[i].kind in ("true", "false"), i
    return tokens[i].lexeme == "true", i + 1


def _kv(tokens: List[Token], i: int) -> Tuple[KV, int]:
    key, _ = _string(tokens, i)
    assert tokens[i + 1].kind == "colon", i
    res = parse(tokens, i + 2)
    if res is None:
        raise RuntimeError(f"wtf i: {i}")
    return (key, res[0]), res[1]


def _object(tokens: List[Token], i: int) -> Tuple[Dict[str, JSON], int]:
    assert tokens[i].kind == "open_brace"
    j = i + 1
    items = []

    while j < len(tokens) and tokens[j].kind != "close_brace":
        item, k = _kv(tokens, j)
        assert k < len(tokens), i
        assert tokens[k].kind in ("comma", "close_brace"), i
        items.append(item)
        if tokens[k].kind == "comma":
            j = k + 1
        else:
            j = k

    # have to end on a close brace or not well formed
    assert j < len(tokens) and tokens[j].kind == "close_brace", i
    return dict(items), j + 1


def _array(tokens: List[Token], i: int) -> Tuple[List[JSON], int]:
    assert tokens[i].kind == "open_bracket"
    j = i + 1
    items = []

    while j < len(tokens) and tokens[j].kind != "close_bracket":
        item, k = parse(tokens, j)
        assert k < len(tokens)
        assert tokens[k].kind in ("comma", "close_bracket")
        items.append(item)
        if tokens[k].kind == "comma":
            j = k + 1
        else:
            j = k

    # have to end on a close bracket or not well formed
    assert j < len(tokens) and tokens[j].kind == "close_bracket", i
    return items, j + 1


def parse(tokens: List[Token], i: int = 0) -> Tuple[Dict, int]:
    token = tokens[i]

    f = {
        "open_brace": _object,
        "open_bracket": _array,
        "number": _number,
        "string": _string,
        "true": _bool,
        "false": _bool,
        "null": _null,
    }[token.kind]

    return f(tokens, i)


__all__ = ["parse"]
