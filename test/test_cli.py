import io
from contextlib import redirect_stdout
from os.path import join as path_join
from pathlib import Path

from remusing_cpp._cli import main

DATA_DIR = path_join(Path(__file__).resolve().parent, "data")


def test_cli():
    test_file = path_join(DATA_DIR, "test.cpp")
    expected = """#include <string>
std::string s;
"""
    f = io.StringIO()
    with redirect_stdout(f):
        main([test_file])
    out = f.getvalue()
    assert out == expected
