"""
This module defines the Edge class, which represents a connection between two
nodes in a network.
The Edge class provides methods to manage and query the properties of the edge,
such as its start node, end node, sign, and whether it is fixed.
"""

from network.node import Node


class Edge:
    """
    Represents an edge in a network, connecting two nodes with a specific sign.
    Provides methods to manage and query the edge's properties.
    """

    def __init__(self, start_node: Node, end_node: Node, sign: int) -> None:
        """
        Initializes an edge with a start node, end node, and sign.
        """
        self.start_node = start_node
        self.end_node = end_node
        self.sign = sign
        self.fixed = False

    def get_start_node(self) -> Node:
        """
        Returns the start node of the edge.
        """
        return self.start_node

    def get_end_node(self) -> Node:
        """
        Returns the end node of the edge.
        """
        return self.end_node

    def get_sign(self) -> int:
        """
        Returns the sign of the edge.
        """
        return self.sign

    def get_fixed(self) -> bool:
        """
        Returns whether the edge is fixed.
        """
        return self.fixed

    def flip_sign(self) -> None:
        """
        Flips the sign of the edge (from 0 to 1 or from 1 to 0).
        """
        self.sign = 1 if self.sign == 0 else 0

    def set_fixed(self) -> None:
        """
        Marks the edge as fixed meaning it cannot change when searching
        for inconsistency solutions.
        """
        self.fixed = True

    def is_equal(self, edge, check_sign: bool) -> bool:
        """
        Checks if this edge is equal to another edge, optionally comparing the
        sign.
        """
        if self.start_node.get_id() != edge.get_start_node().get_id() or \
                self.end_node.get_id() != edge.get_end_node().get_id():
            return False
        if check_sign:
            return self.sign == edge.get_sign()
        return True
