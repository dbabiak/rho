import io
from contextlib import contextmanager


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
