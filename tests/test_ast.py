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


def test_typecheck_basic_successes():
    assert Print(Literal(0)).typecheck() is None
    assert BASIC_PROGRAM.typecheck() is None


def test_typecheck_basic_failures():
    expected = RhoTypeError(msg="Plus.right is not a number: Print(val=Literal(val=7))")
    actual = Plus(Literal(0), Print(Literal(7))).typecheck()
    assert expected == actual


def test_basic_ast_transform():
    program = BASIC_PROGRAM_WITH_EVENS
    linted: AST = no_evens(program)
    compiled = linted.compile()
    assert compiled == "print(((13 * (3 + 1)) + (int(input()) * 7)))"


# not really a full blown random ast
# but given topology but with a literal node with a random value
@given(ast_n=integers(), input_n=integers())
def test_transform_random_ast(ast_n: int, input_n):
    program = Print(
        Plus(Times(Literal(13), Literal(ast_n)), Times(GetNumber(), Literal(7)))
    )
    linted: AST = no_evens(program)
    expected = run(program, _input=input_n)
    actual = run(linted, _input=input_n)

    if is_even(ast_n):
        assert program != linted
    else:
        assert program == linted

    assert expected == actual
