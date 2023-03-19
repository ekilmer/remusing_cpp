"""
This module contains classes that build tree-sitter queries.
"""


class TypeQuery:
    """
    A class to build tree-sitter queries to capture unqualified and qualified
    type identifiers.
    """

    def __init__(self) -> None:
        """
        Initialize the tree-sitter query builder for capturing types. You may
        change the capture names by setting the appropriate instance variables.
        """
        self.TYPE_ALL_CAPTURE = "type"
        """Capture name for _all_ type identifiers"""
        self.TYPE_QUAL_CAPTURE = "type_qual"
        """Capture name for qualified type identifiers"""
        self.TYPE_SCOPE_CAPTURE = "type_scope"
        """Capture name for scope name of qualified type identifiers"""
        self.TYPE_QUAL_TEMPLATE_CAPTURE = "type_qual_template"
        self.TYPE_SCOPE_TEMPLATE_CAPTURE = "type_scope_template"

    def build_all_type_query(self) -> str:
        """
        Build a query to match all `type_identifier` nodes. This includes
        qualified types.

        Returns:
            A query string to pass to tree-sitter
        """
        return f"""
        (
          (type_identifier) @{self.TYPE_ALL_CAPTURE}
        )
        """

    def build_qualified_type_query(self) -> str:
        """
        Build a query to select all qualified types.

        Returns:
            A query string to pass to tree-sitter
        """
        return f"""
        (
          (qualified_identifier
            scope: (namespace_identifier) @{self.TYPE_SCOPE_CAPTURE}
            name: (type_identifier) @{self.TYPE_QUAL_CAPTURE}
          )
        )
        """

    def build_qualified_template_type_query(self) -> str:
        """
        Build a query to select all qualified types used in a template.

        Returns:
            A query string to pass to tree-sitter
        """
        return f"""
        (
          (qualified_identifier
            scope: (namespace_identifier) @{self.TYPE_SCOPE_TEMPLATE_CAPTURE}
            name:
              (template_type
                name: (type_identifier) @{self.TYPE_QUAL_TEMPLATE_CAPTURE}
              )
          )
        )
        (
          (qualified_identifier
            scope: (namespace_identifier) @{self.TYPE_SCOPE_TEMPLATE_CAPTURE}
            name:
              (qualified_identifier
                scope: (template_type name: (type_identifier) @{self.TYPE_QUAL_TEMPLATE_CAPTURE})
                name: (type_identifier) @{self.TYPE_QUAL_TEMPLATE_CAPTURE}
              )
          )
        )
        """

    def build_all_queries(self) -> str:
        """
        Build all queries and combine into one.

        Returns:
            All queries as a single string to pass to tree-sitter
        """
        return f"""
        {self.build_all_type_query()}
        {self.build_qualified_type_query()}
        {self.build_qualified_template_type_query()}
        """


class SymbolQuery:
    """
    A class to build tree-sitter queries to capture unqualified symbol names.
    """

    def __init__(self) -> None:
        """
        Initialize the tree-sitter query builder for capturing symbols. You may
        change the capture names by setting the appropriate instance variables.
        """
        self.SYMBOL_CAPTURE = "symbol"
        """Capture name for unqualified symbols used in expressions"""
        self.SYMBOL_FUNC_CAPTURE = "func"
        """Capture name for unqualified symbols used in function calls"""
        self._SYMBOL_STREAM_CAPTURE = "stream"
        """
        Private capture name for `iostream` symbol query. In case you need to
        change it to prevent naming conflicts
        """

    def build_stream_symbol_query(self) -> str:
        """
        Build a query to capture unqualified symbols in `iostream` operators.

        Returns:
            A query string to pass to tree-sitter
        """
        return f"""
        (
            (binary_expression
                right: (identifier) @{self.SYMBOL_CAPTURE}
            ) @{self._SYMBOL_STREAM_CAPTURE}
            (#match? @{self._SYMBOL_STREAM_CAPTURE} "<<")
        )
        (
            (binary_expression
                left: (identifier) @{self.SYMBOL_CAPTURE}
            ) @{self._SYMBOL_STREAM_CAPTURE}
            (#match? @{self._SYMBOL_STREAM_CAPTURE} "(<<)|(>>)")
        )
        """

    def build_function_symbol_query(self) -> str:
        """
        Build a query to capture unqualified symbols used in function calls.

        Returns:
            A query string to pass to tree-sitter
        """
        return f"""
        (call_expression
          function: (
            template_function
              name: (identifier) @{self.SYMBOL_FUNC_CAPTURE}
          )
        )
        (call_expression
          function: (identifier) @{self.SYMBOL_FUNC_CAPTURE}
        )
        """

    def build_all_queries(self) -> str:
        """
        Build all queries and combine into one.

        Returns:
            All queries as a single string to pass to tree-sitter
        """
        return f"""
        {self.build_stream_symbol_query()}
        {self.build_function_symbol_query()}
        """


class UsingQuery:
    """
    A class to build tree-sitter queries to capture `using` statements.
    """

    def __init__(self) -> None:
        """
        Initialize the tree-sitter query builder for capturing `using`
        statements. You may change the capture names by setting the appropriate
        instance variables.
        """
        self.USING_QUAL_TYPE_CAPTURE = "using_qual_type"
        """
        Capture name for the qualified type in a `using` declaration, e.g.
        `std::string` in `using std::string;`
        """
        self.USING_DECL_CAPTURE = "using_decl"
        """Capture name for qualified `using` declarations."""
        self.USING_IDENT_CAPTURE = "using_id"
        """
        Capture name for `identifier` in a `using` declaration, e.g. `std` in
        `using namespace std;`
        """
        self.USING_NS_DECL_CAPTURE = "using_ns_decl"
        """
        Capture name for a `using` namespace declaration, e.g.
        `using namespace std;`
        """

    def build_using_qual_type_query(self) -> str:
        """
        Build a query to select all `using` qualified type statements.

        Returns:
            A query to pass to tree-sitter
        """
        return f"""
        (
          (using_declaration
            (qualified_identifier) @{self.USING_QUAL_TYPE_CAPTURE}
          ) @{self.USING_DECL_CAPTURE}
        )
        """

    def build_using_ns_query(self) -> str:
        """
        Build a query to select all `using namespace` statements.

        Returns:
            A query to pass to tree-sitter
        """
        return f"""
        (
          (using_declaration
            (identifier) @{self.USING_IDENT_CAPTURE}
          ) @{self.USING_NS_DECL_CAPTURE}
        )
        """

    def build_all_queries(self) -> str:
        """
        Build all queries and combine into one.

        Returns:
            All queries as a single string to pass to tree-sitter
        """
        return f"""
        {self.build_using_qual_type_query()}
        {self.build_using_ns_query()}
        """
