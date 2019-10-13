from dataclasses import dataclass
from typing import *
from operator import add, mul


@dataclass
class AST:
    def eval(self) -> Any:
        pass

    def optimize(self) -> "AST":
        return self

    def compile(self) -> str:
        pass


@dataclass
class Print(AST):
    val: AST

    def eval(self) -> Any:
        print(self.val.eval())

    def optimize(self) -> "AST":
        return type(self)(self.val.optimize())

    def compile(self):
        return f"print({self.val.compile()})"


@dataclass
class Plus(AST):
    left: AST
    right: AST
    _op = add

    def eval(self) -> int:
        return self.left.eval() + self.right.eval()

    def optimize(self) -> AST:
        left = self.left.optimize()
        right = self.right.optimize()
        if isinstance(left, Literal) and isinstance(right, Literal):
            val = self._op(left.val, right.val)
            return Literal(val)
        else:
            return type(self)(left, right)

    def compile(self) -> str:
        return f"({self.left.compile()} + {self.right.compile()})"


@dataclass
class Times(AST):
    left: AST
    right: AST
    _op = mul

    def eval(self) -> int:
        return self._op(self.left.eval(), self.right.eval())

    def optimize(self) -> AST:
        left = self.left.optimize()
        right = self.right.optimize()
        if isinstance(left, Literal) and isinstance(right, Literal):
            val = self._op(left.val, right.val)
            return Literal(val)
        else:
            return type(self)(left, right)

    def compile(self) -> str:
        return f"({self.left.compile()} * {self.right.compile()})"


@dataclass
class Literal(AST):
    val: int

    def eval(self) -> int:
        return self.val

    def compile(self) -> str:
        return str(self.val)


@dataclass
class GetNumber(AST):
    def eval(self) -> int:
        return int(input())

    def compile(self) -> str:
        return "int(input())"


BASIC_PROGRAM = Print(
    Plus(Times(Literal(13), Literal(2)), Times(GetNumber(), Literal(7)))
)
B = BASIC_PROGRAM
