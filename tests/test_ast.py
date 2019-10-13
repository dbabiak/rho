from hypothesis import given
from hypothesis.strategies import integers

from rho.ast import *
from rho.ast import AST, Print
from tests import run_thunk, run, run_eval

import hypothesis
from hypothesis import settings
settings.register_profile(
    "dev", max_examples=10, verbosity=hypothesis.Verbosity.verbose
)


@given(n=integers())
def test_eval_basic2(n: int):
    expected = run_eval("print(13 * 2 + int(input()) * 7)", _input=n)
    actual = run(BASIC_PROGRAM, _input=n)
    assert expected == actual


@given(n=integers())
def test_eval_basic(n: int):
    expected = run_thunk(lambda: print(13 * 2 + int(input()) * 7), _input=n)
    actual = run(BASIC_PROGRAM, _input=n)
    assert expected == actual


@given(n=integers())
def test_optimize_basic(n: int):
    program: Print = BASIC_PROGRAM
    optimized: AST = program.optimize()

    expected = run(BASIC_PROGRAM, _input=n)
    actual = run(optimized, _input=n)

    assert expected == actual


def test_compile_basic():
    program: Print = BASIC_PROGRAM
    compiled: str = program.compile()
    assert compiled == "print(((13 * 2) + (int(input()) * 7)))"


@given(n=integers())
def test_compile_eval_basic(n: int):
    program: Print = BASIC_PROGRAM
    compiled: str = program.compile()

    expected = run(BASIC_PROGRAM, _input=n)
    actual = run_eval(compiled, _input=n)
    assert expected == actual
