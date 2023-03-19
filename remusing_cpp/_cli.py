"""
The `remusing_cpp` entrypoint.
"""

import argparse
import locale
import os
import sys
import tempfile
from pathlib import Path
from typing import List

from remusing_cpp.core import RemUsing
from remusing_cpp.util import build_cpp_parser


def build_argparser() -> argparse.ArgumentParser:
    """
    Build a CLI argument parser for the project.

    Returns:
        A parser that can handle the CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Remove and refactor 'using' declarations in C++ files",
    )
    parser.add_argument(
        "infile",
        help="C++ file input (default: stdin)",
        nargs="?",
        type=argparse.FileType("rb"),
        default=(None if sys.stdin.isatty() else sys.stdin),
    )
    parser.add_argument(
        "outfile",
        help="Refactored C++ file output (default: stdout)",
        nargs="?",
        type=argparse.FileType("wb"),
        default=sys.stdout,
    )
    parser.add_argument(
        "-i", "--in-place", action="store_true", help="Overwrite input file with changes"
    )
    parser.add_argument(
        "-t",
        "--ts-source",
        type=str,
        help="Tree-sitter C++ source code repo directory (default: %(default)s)",
        default=os.path.join(Path(__file__).resolve().parent, "vendor", "tree-sitter-cpp"),
    )
    parser.add_argument(
        "-s",
        "--ts-out",
        type=str,
        help="Tree-sitter language output file (default: %(default)s)",
        default=os.path.join(tempfile.gettempdir(), "ts_cpp_language"),
    )
    parser.add_argument("--init", action="store_true", help="Initialize tree-sitter library only")
    return parser


def validate_args(args: argparse.Namespace) -> bool:
    """
    Validate the arguments from the CLI. Sometimes there are incompatible
    options, and this function will identify these incompatibilities.

    This function also adjusts arguments to prevent mistakes that might be easy
    to make. For instance, writing in-place doesn't make sense when the input
    comes from `stdin`, so we silently fix that without error.

    Returns:
        Whether the arguments are compatible or not.
    """
    if args.in_place and args.outfile != sys.stdout:
        print("Cannot have both 'in-place' option and outfile argument", file=sys.stderr)
        return False
    if args.in_place and args.infile == sys.stdin:
        # Cannot write in-place to stdin but this is silent
        args.in_place = False
    if args.infile is None:
        print("Input file not specified!")
        return False
    return True


def main(argv: List[str] = sys.argv[1:]) -> int:
    """
    Entry-point for the CLI entry-point.

    Arguments:
        argv: Argument list to process

    Returns:
        Exit code
    """
    # --- Arg parsing
    argparser = build_argparser()
    args = argparser.parse_args(argv)
    if args.init:
        print("Initializing tree-sitter library...")
        print(f"\tsource: {args.ts_source}")
        print(f"\toutput: {args.ts_out}")
        build_cpp_parser(args.ts_source, args.ts_out)
        print("Built!")
        return 0
    if not validate_args(args):
        argparser.print_help(sys.stdout)
        return 1

    if args.infile == sys.stdin:
        src = args.infile.read().encode(locale.getpreferredencoding())
    else:
        src = args.infile.read()
    args.infile.close()

    # --- App logic
    parser, language = build_cpp_parser(args.ts_source, args.ts_out)
    output = RemUsing(src, parser, language).fix()

    # --- Output
    if args.in_place:
        with open(args.infile.name, "wb") as o:
            o.write(output)
    else:
        if args.outfile == sys.stdout:
            args.outfile.write(output.decode(locale.getpreferredencoding()))
        else:
            args.outfile.write(output)
        args.outfile.flush()

    return 0
