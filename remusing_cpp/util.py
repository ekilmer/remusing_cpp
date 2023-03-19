"""
This module contains helpful utility functions for interacting with tree-sitter
and preparing for usage of the library.
"""
from typing import Tuple

from tree_sitter import Language, Parser


def build_cpp_language(tree_sitter_cpp_path: str, out_path: str) -> Language:
    """
    Build the C++ tree-sitter language.

    Args:
        tree_sitter_cpp_path: Where to look for the tree sitter C++ repo
        out_path: Where to place the built langauge

    Returns:
        The built language
    """
    Language.build_library(out_path, [tree_sitter_cpp_path])
    return Language(out_path, "cpp")


def build_cpp_parser(tree_sitter_cpp_path: str, out_path: str) -> Tuple[Parser, Language]:
    """
    Build the C++ tree -itter parser.

    Args:
        tree_sitter_cpp_path: Where to look for the tree-sitter C++ repo
        out_path: Where to place the built langauge

    Returns:
        A C++ tree-sitter parser
    """
    language = build_cpp_language(tree_sitter_cpp_path, out_path)
    parser = Parser()
    parser.set_language(language)
    return parser, language
