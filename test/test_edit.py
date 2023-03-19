from tree_sitter import Language, Parser

from remusing_cpp.core import RemUsing
from remusing_cpp.util import build_cpp_parser


def test_hardcoded_w_using_ns_replace(language, parser):
    src = bytes(
        """using namespace std;
string s;
        """,
        "utf8",
    )
    expected = bytes(
        """std::string s;
        """,
        "utf8",
    )
    remusing = RemUsing(src, parser, language)
    remusing.hardcoded_namespace_map = {"string": "std"}
    output = remusing.fix()
    assert output == expected


def test_hardcoded_wo_using_ns_replace(language, parser):
    src = bytes(
        """string s;""",
        "utf8",
    )
    expected = bytes(
        """std::string s;""",
        "utf8",
    )
    remusing = RemUsing(src, parser, language)
    remusing.hardcoded_namespace_map = {"string": "std"}
    output = remusing.fix()
    assert output == expected


def test_using_decl_replace(language, parser):
    src = bytes(
        """
using std::foo;
foo f;
""",
        "utf8",
    )
    expected = bytes(
        """
std::foo f;
""",
        "utf8",
    )
    output = RemUsing(src, parser, language).fix()
    assert output == expected


def test_no_replace(language, parser):
    src = bytes(
        """custom s;""",
        "utf8",
    )
    expected = bytes(
        """custom s;""",
        "utf8",
    )
    remusing = RemUsing(src, parser, language)
    remusing.hardcoded_namespace_map = {}
    output = remusing.fix()
    assert output == expected


def test_util_func(language_out: str, cpp_tree_sitter_repo: str):
    parser, language = build_cpp_parser(cpp_tree_sitter_repo, language_out)
    test_edit(language, parser)


def test_std_functions(language: Language, parser: Parser) -> None:
    src = bytes(
        """
using std::min;
min(3, 2);
        """,
        "utf8",
    )
    expected = bytes(
        """
std::min(3, 2);
        """,
        "utf8",
    )
    out = RemUsing(src, parser, language).fix()
    assert out == expected


def test_noop_template(language: Language, parser: Parser) -> None:
    src = bytes(
        """
mutable typename std::list<_recordtype>::iterator value;
        """,
        "utf8",
    )
    expected = bytes(
        """
mutable typename std::list<_recordtype>::iterator value;
        """,
        "utf8",
    )
    out = RemUsing(src, parser, language).fix()
    assert out == expected


def test_std_stream_functions(language: Language, parser: Parser) -> None:
    src = bytes(
        """
using std::hex;
cout << "0x" << hex << val << "";
        """,
        "utf8",
    )
    expected = bytes(
        """
std::cout << "0x" << std::hex << val << "";
        """,
        "utf8",
    )
    out = RemUsing(src, parser, language).fix()
    assert out == expected


def test_edit(language, parser):
    src = bytes(
        """using my::own::string;
using fake::vector;
using namespace std;
vector v;
std::vector v2;
string s;
keep::vector<string> t;
keep::map<string, std::string> t;
custom<string, std::string, vector<string<keep::map, vector>>> t;
custom<string, vector<string<keep::map, vector>>> t;
    """,
        "utf8",
    )
    expected = bytes(
        """fake::vector v;
std::vector v2;
my::own::string s;
keep::vector<my::own::string> t;
keep::map<my::own::string, std::string> t;
custom<string, std::string, fake::vector<my::own::string<keep::map, fake::vector>>> t;
custom<string, fake::vector<my::own::string<keep::map, fake::vector>>> t;
    """,
        "utf8",
    )
    remusing = RemUsing(src, parser, language)
    remusing.parse()
    remusing.query()
    remusing.process_captures()
    output = remusing.fix()
    assert output == expected
