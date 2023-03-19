"""
This module is the core of functionality for the library.
"""
from typing import Dict, List, Optional, Set, Tuple

from tree_sitter import Language, Node, Parser, Tree

from remusing_cpp.queries import SymbolQuery, TypeQuery, UsingQuery
from remusing_cpp.symbols import (
    get_default_std_symbols,
    get_default_symb_namespace_map,
)
from remusing_cpp.ts_model import HashableTreeNode


class RemUsing:
    """
    Class to remove `using` declarations and refactor symbol names.
    """

    def __init__(self, src: bytes, parser: Parser, language: Language):
        """
        Initialize the class.

        Arguments:
            src: The starting C++ source code
            parser: The C++ tree-sitter parser
            language: The C++ tree-sitter language
        """
        self.src = src
        self.parser = parser
        self.language = language

        self.types_query = TypeQuery()
        self.symbols_query = SymbolQuery()
        self.using_query = UsingQuery()

        self.find_symbols = get_default_std_symbols()
        self.hardcoded_namespace_map = get_default_symb_namespace_map()

        self._tree: Optional[Tree] = None
        self._query_str: Optional[str] = None
        self._captures: Optional[List[Tuple[Node, str]]] = None
        self._lookup_captures: Optional[Dict[str, Set[HashableTreeNode]]] = None
        self._unqualified_types: Optional[List[HashableTreeNode]] = None
        self._decl_ns_map: Optional[Dict[str, str]] = None

        # API State tracking
        self._did_parse = False
        self._did_query = False
        self._did_process_captures = False
        self._did_fix = False

    def parse(self) -> None:
        """
        Parse the source code with tree-sitter.
        """
        if self._did_parse:
            return

        self._tree = self.parser.parse(self.src)

        self._did_parse = True

    def query(self) -> None:
        """
        Run tree-sitter queries on the parsed source code to gather necessary
        information about qualified/unqualified symbols and `using` statements.
        """
        if self._did_query:
            return
        else:
            self.parse()

        self._query_str = "\n".join(
            [
                self.types_query.build_all_queries(),
                self.symbols_query.build_all_queries(),
                self.using_query.build_all_queries(),
            ]
        )
        query = self.language.query(self._query_str)
        assert self._tree is not None
        self._captures = query.captures(self._tree.root_node)

        self._did_query = True

    def process_captures(self) -> None:
        """
        Process the captured elements that we queried and enable our fixes.
        """
        if self._did_process_captures:
            return
        else:
            self.query()

        # Collect all captures into a workable representation
        self._lookup_captures = {}
        assert self._captures is not None
        for cap in self._captures:
            cap_node: Node = cap[0]
            cap_name: str = cap[1]
            if cap_name not in self._lookup_captures:
                self._lookup_captures[cap_name] = {HashableTreeNode(cap_node)}
            else:
                self._lookup_captures[cap_name].add(HashableTreeNode(cap_node))

        # Gather unqualified identifiers
        all_types = self._lookup_captures.get(self.types_query.TYPE_ALL_CAPTURE, set())
        self._unqualified_types = sorted(
            set.union(
                # We collected _all_ type_identifiers, so we need to filter out the qualified ones
                all_types.difference(
                    set.union(
                        self._lookup_captures.get(self.types_query.TYPE_QUAL_CAPTURE, set()),
                        self._lookup_captures.get(
                            self.types_query.TYPE_QUAL_TEMPLATE_CAPTURE, set()
                        ),
                    )
                ),
                self._lookup_captures.get(self.symbols_query.SYMBOL_CAPTURE, set()),
                self._lookup_captures.get(self.symbols_query.SYMBOL_FUNC_CAPTURE, set()),
            )
        )

        # Map of `using` qualified-type declarations from type to namespace
        self._decl_ns_map = {}
        for decl in self._lookup_captures.get(self.using_query.USING_QUAL_TYPE_CAPTURE, []):
            node = decl.node
            name_node = node.child_by_field_name("name")
            scope_node = node.child_by_field_name("scope")
            name = ""
            scope = []

            # Handle nested scope namespace
            while scope_node and name_node:
                name = name_node.text.decode("utf8")
                scope.append(scope_node.text.decode("utf8"))

                scope_node = name_node.child_by_field_name("scope")
                name_node = name_node.child_by_field_name("name")

            scope_text = "::".join(scope)
            self._decl_ns_map[name] = scope_text

        self._did_process_captures = True

    def fix(self) -> bytes:
        """
        Fix the source code to remove `using` declarations and add namespace
        qualifications to the unqualified symbols.

        Returns:
            The new fixed source code.
        """
        self.process_captures()

        output = b""
        out_idx = 0

        assert self._tree is not None
        assert self._lookup_captures is not None
        assert self._unqualified_types is not None
        assert self._decl_ns_map is not None

        # Need to sort so that it makes creating the new text easier in one go
        using_decls = self._lookup_captures.get(self.using_query.USING_DECL_CAPTURE, set())
        using_ns = self._lookup_captures.get(self.using_query.USING_NS_DECL_CAPTURE, set())
        fixups = sorted(set.union(set(self._unqualified_types), using_decls, using_ns))
        for node in fixups:
            start_byte = node.node.start_byte
            start_txt = self._tree.text[out_idx:start_byte].decode("utf8")

            if node.node.type == "using_declaration":
                # Remove these nodes from the output text
                output += start_txt.encode("utf8")
                out_idx = node.node.end_byte
                # Skip newline-like characters
                while chr(self._tree.text[out_idx]) in {"\n", "\r"}:
                    out_idx += 1
            elif node.node.type in {"type_identifier", "identifier"}:
                end_txt = self._tree.text[node.node.start_byte : node.node.end_byte].decode("utf8")
                out_idx = node.node.end_byte

                # Lookup namespace from existing 'using <decl>'
                ns = self._decl_ns_map.get(node.text, "")
                hard = self.hardcoded_namespace_map.get(node.text, None)
                if ns:
                    # Insert into text
                    output += f"{start_txt}{ns}::{end_txt}".encode()
                elif hard:
                    # Maybe it's a hardcoded mapping (to handle 'using namespace <id>')
                    output += f"{start_txt}{hard}::{end_txt}".encode()
                else:
                    # print(f"WARN: Could not find qualifier for type {node.text}")
                    output += f"{start_txt}{end_txt}".encode()
            else:  # pragma: no cover
                print(f"ERROR: Not processing unknown node type: {node.node.type}")
        output += self._tree.text[out_idx:]

        self._did_fix = True

        return output
