import io
from contextlib import contextmanager
from dataclasses import dataclass
from numbers import Number
import sys
from typing import *


@dataclass
class AST:
    def eval(self) -> Any:
        pass


@dataclass
class Print(AST):
    val: AST

    def eval(self) -> Any:
        print(self.val.eval())

@dataclass
class Plus(AST):
    left: AST
    right: AST

    def eval(self) -> Number:
        return self.left.eval() + self.right.eval()


@dataclass
class Times(AST):
    left: AST
    right: AST

    def eval(self) -> Number:
        return self.left.eval() * self.right.eval()


@dataclass
class Literal(AST):
    val: Number

    def eval(self) -> Number:
        return self.val


@dataclass
class GetNumber(AST):
    def eval(self) -> Number:
        return int(input(""))


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
