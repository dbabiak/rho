from db.ast_demo import *

import hypothesis.strategies


@hypothesis.given(hypothesis.strategies.integers())
# @hypothesis.settings(verbosity=hypothesis.Verbosity.verbose)
def test_eval_basic_program(n: int):
    program = Print(
        Plus(Times(Literal(13), Literal(2)), Times(GetNumber(), Literal(7)))
    )
    out: io.StringIO
    with stdin_input_of(str(n)), stdout() as out:
        print(13 * 2 + int(input()) * 7)
        out.seek(0)
        expected = out.read()

    with stdin_input_of(str(n)), stdout() as out:
        program.eval()
        out.seek(0)
        actual = out.read()


    print(f'n: {n} -> {expected}')
    assert expected == actual


test_eval_basic_program()
