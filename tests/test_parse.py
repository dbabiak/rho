from pox.func_parse import (
    lex_and_parse,
    to_json,
    Program,
    Function,
    Block,
    Return,
    Binary,
    Identifier,
)
from operator import mul


def test_parse_function():
    src = """
    fun multiply(x, y) {
      return x * y;
    }
    """

    ast = lex_and_parse(src)

    assert ast == Program(
        statements=(
            Function(
                name="multiply",
                parameters=["x", "y"],
                body=Block(
                    statements=(
                        Return(
                            expr=Binary(
                                operator=mul,
                                left=Identifier(symbol="x"),
                                right=Identifier(symbol="y"),
                            )
                        ),
                    )
                ),
            ),
        )
    )
