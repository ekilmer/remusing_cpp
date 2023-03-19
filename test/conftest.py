import os
import tempfile
from pathlib import Path
from typing import Final

import pytest
from tree_sitter import Language, Parser

from remusing_cpp.util import build_cpp_language

LANGUAGE_OUT_PATH: Final[str] = os.path.join(tempfile.gettempdir(), "ts_cpp_language")
CPP_TREE_SITTER_PATH: Final[str] = os.path.join(
    Path(__file__).resolve().parent.parent, "remusing_cpp", "vendor", "tree-sitter-cpp"
)


@pytest.fixture
def language_out() -> str:
    """
    Output for compiled tree-sitter language

    Returns:
        Path to tree-sitter compiled output file

    """
    return LANGUAGE_OUT_PATH


@pytest.fixture
def cpp_tree_sitter_repo() -> str:
    """
    Path to C++ tree-sitter repo

    Returns:
        Path to tree-sitter language repo
    """
    return CPP_TREE_SITTER_PATH


@pytest.fixture
def language(language_out: str, cpp_tree_sitter_repo: str) -> Language:
    """
    C++ tree-sitter language

    Args:
        language_out: Output for compiled tree-sitter language
        cpp_tree_sitter_repo: Path to C++ tree-sitter repo

    Returns:
        C++ tree-sitter language
    """
    return build_cpp_language(cpp_tree_sitter_repo, language_out)


@pytest.fixture
def parser(language: Language) -> Parser:
    """
    C++ tree-sitter parser

    Args:
        language: C++ language for the parser

    Returns:
        A C++ tree-sitter parser
    """
    parser = Parser()
    parser.set_language(language)
    return parser
