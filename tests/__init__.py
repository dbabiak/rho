import io
from contextlib import contextmanager
from typing import *
from typing import Any

import hypothesis


from rho.ast import AST

hypothesis.settings.register_profile(
    "dev", max_examples=10, verbosity=hypothesis.Verbosity.verbose
)


@contextmanager
def stdin_input_of(s: str):
    assert isinstance(s, str) and len(s) > 0
    import sys

    _stdin = sys.stdin
    try:
        stream = io.StringIO()
        stream.write(s)
        if s[-1] != "\n":
            stream.write("\n")
        stream.seek(0)
        sys.stdin = stream
        yield
    finally:
        sys.stdin = _stdin


@contextmanager
def stdout() -> io.StringIO:
    import sys

    _stdout = sys.stdout
    try:
        stream = io.StringIO()
        sys.stdout = stream
        yield stream
    finally:
        sys.stdout = _stdout


def run_eval(code: str, _input: Any) -> str:
    out: io.StringIO
    with stdin_input_of(str(_input)), stdout() as out:
        eval(code)
        out.seek(0)
        return out.read()


def run_thunk(f: Callable, _input: Any) -> str:
    out: io.StringIO
    with stdin_input_of(str(_input)), stdout() as out:
        f()
        out.seek(0)
        return out.read()


def run(program: AST, _input: Any) -> str:
    with stdin_input_of(str(_input)), stdout() as out:
        program.eval()
        out.seek(0)
        return out.read()
