"""
This module contains custom data models to improve upon the original tree sitter
data types.
"""
from dataclasses import dataclass
from functools import total_ordering
from typing import Any

from tree_sitter import Node


@total_ordering
@dataclass
class HashableTreeNode:
    """
    A tree-sitter node that is hashable for use in Sets.
    """

    node: Node

    @property
    def text(self) -> str:
        """
        Get the source code text for this node.

        Returns:
            String text for this node.
        """
        return self.node.text.decode("utf8")

    def __hash__(self) -> int:
        """
        Calculate the hash.
        """
        return hash((self.node.start_point, self.node.end_point))

    def __eq__(self, other: Any) -> bool:
        """
        Check for equality.
        """
        if isinstance(other, HashableTreeNode):
            return (self.node.start_point, self.node.end_point) == (
                other.node.start_point,
                other.node.end_point,
            )
        return False  # pragma: no cover

    def __lt__(self, other: Any) -> bool:
        """
        Check for less-than.
        """
        if not isinstance(other, HashableTreeNode):  # pragma: no cover
            return NotImplemented
        return (self.node.start_point, self.node.end_point) < (
            other.node.start_point,
            other.node.end_point,
        )
