from dataclasses import dataclass
from typing import *
from operator import add, mul
from functools import partial


@dataclass
class RhoTypeError(Exception):
    msg: str


@dataclass
class AST:
    def eval(self) -> Any:
        pass

    def optimize(self) -> "AST":
        return self

    def compile(self) -> str:
        pass

    def typecheck(self) -> Optional[RhoTypeError]:
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

    def typecheck(self) -> Optional[RhoTypeError]:
        return self.val.typecheck()


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

    def typecheck(self) -> Optional[RhoTypeError]:
        if not is_numeric(self.left):
            return RhoTypeError(f"Plus.left is not a number: {self.left}")

        if not is_numeric(self.right):
            return RhoTypeError(f"Plus.right is not a number: {self.right}")

        return self.left.typecheck() or self.right.typecheck()


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

    def typecheck(self) -> Optional[RhoTypeError]:
        if not is_numeric(self.left):
            return RhoTypeError(f"Times.left is not a number: {self.left}")

        if not is_numeric(self.right):
            return RhoTypeError(f"Times.right is not a number: {self.right}")

        return self.left.typecheck() or self.right.typecheck()


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


def is_numeric(e: AST) -> bool:
    return isinstance(e, (Plus, Times, Literal, GetNumber))


def children(node: AST) -> Iterable[AST]:
    if isinstance(node, (GetNumber, Literal)):
        return tuple()

    if isinstance(node, (Plus, Times)):
        return node.left, node.right

    if isinstance(node, Print):
        return (node.val,)


def transform(
    node: AST, predicate: Callable[[AST], bool], f: Callable[[AST], AST]
) -> AST:
    if predicate(node):
        return f(node)

    _children = children(node)
    if not _children:
        return node
    else:
        f_children = (transform(c, predicate, f) for c in _children)
        return type(node)(*f_children)


def is_even(n: int):
    return abs(n) != 2 and n % 2 == 0


no_evens = partial(
    transform,
    predicate=lambda node: isinstance(node, Literal) and is_even(node.val),
    f=lambda node: Plus(Literal((node.val // 2) + 1), Literal((node.val // 2) - 1)),
)

BASIC_PROGRAM = Print(
    Plus(Times(Literal(13), Literal(2)), Times(GetNumber(), Literal(7)))
)

BASIC_PROGRAM_WITH_EVENS = Print(
    Plus(Times(Literal(13), Literal(4)), Times(GetNumber(), Literal(7)))
)

B = BASIC_PROGRAM
BE = BASIC_PROGRAM_WITH_EVENS
