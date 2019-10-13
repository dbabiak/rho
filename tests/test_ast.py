import io

import hypothesis.strategies

from rho.ast import *
from tests import stdin_input_of, stdout

BASIC_PROGRAM = Print(
    Plus(Times(Literal(13), Literal(2)), Times(GetNumber(), Literal(7)))
)


@hypothesis.given(n=hypothesis.strategies.integers())
@hypothesis.settings(
    max_examples=20,
    # verbosity=hypothesis.Verbosity.verbose,
)
def test_eval_basic_program(n: int):
    program = BASIC_PROGRAM
    out: io.StringIO
    with stdin_input_of(str(n)), stdout() as out:
        print(13 * 2 + int(input()) * 7)
        out.seek(0)
        expected = out.read()

    with stdin_input_of(str(n)), stdout() as out:
        program.eval()
        out.seek(0)
        actual = out.read()

    print(f"n: {n} -> {expected}")
    assert expected == actual, f"{expected} != {actual}"


@hypothesis.given(n=hypothesis.strategies.integers())
@hypothesis.settings(
    max_examples=20,
    # verbosity=hypothesis.Verbosity.verbose,
)
def test_optimize_basic_program(n: int):
    program = BASIC_PROGRAM
    optimized = program.optimize()
    out: io.StringIO
    with stdin_input_of(str(n)), stdout() as out:
        program.eval()
        out.seek(0)
        expected = out.read()

    with stdin_input_of(str(n)), stdout() as out:
        optimized.eval()
        out.seek(0)
        actual = out.read()

    print(f"n: {n} -> {expected}")
    assert expected == actual, f"{expected} != {actual}"


# test_eval_basic_program()
test_optimize_basic_program()
