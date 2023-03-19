"""
This file contains tests with known bugs. The tests should include assertions
for BOTH the correct operation and current incorrect operation so that we can
detect when functionality changes and move the test(s) out of this file when
they are fixed.
"""
from tree_sitter import Language, Parser

from remusing_cpp.core import RemUsing


def test_nested_templates(language: Language, parser: Parser) -> None:
    """
    There is a bug in tree-sitter with nested template arguments.

    See https://github.com/tree-sitter/tree-sitter-cpp/issues/192
    """
    src = bytes("map<string, vector<vector<string>>> v;", "utf8")

    remusing = RemUsing(src, parser, language)
    remusing.process_captures()

    # fmt: off
    expected_matches = ["map", "string", "vector", "vector", "string"]
    actual_matches =   ["map",           "vector", "vector", "string"]
    # fmt: on

    unqual_names = [node.text for node in remusing._unqualified_types]

    if unqual_names == expected_matches:
        assert False, "This works now! Change the test"
    assert unqual_names == actual_matches


def test_undeclared_identifier_arg(language: Language, parser: Parser) -> None:
    src = bytes(
        """
#include <cstdio>
#include <iostream>
using namespace std;
int main() {
    std::ostream& Cout = cout;
    return 0;
}
    """,
        "utf8",
    )
    expected = bytes(
        """
#include <cstdio>
#include <iostream>
int main() {
    std::ostream& Cout = std::cout;
    return 0;
}
    """,
        "utf8",
    )
    actual = bytes(
        """
#include <cstdio>
#include <iostream>
int main() {
    std::ostream& Cout = cout;
    return 0;
}
    """,
        "utf8",
    )
    out = RemUsing(src, parser, language).fix()
    if out == expected:
        assert False, "This test works now! Change the test"
    assert out == actual
