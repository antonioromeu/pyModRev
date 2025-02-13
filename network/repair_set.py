"""
This module defines the Repair_Set class, which represents a set of repairs
for inconsistencies in a network.
The class provides methods to manage and analyze repaired functions, flipped
edges, removed edges, and added edges.
"""

from typing import List
from network.edge import Edge
from network.function import Function


class Repair_Set:
    """
    Represents a set of repairs for inconsistencies in a network.
    Provides methods to manage repaired functions, flipped edges, removed
    edges, and added edges.
    """
    def __init__(self):
        """
        Initializes an empty repair set with no repaired functions, edges, or
        operations.
        """
        self.repaired_functions = []  # List of Functions
        self.flipped_edges = []  # List of Edges
        self.removed_edges = []  # List of Edges
        self.added_edges = []  # List of Edges
        self.n_topology_changes = 0
        self.n_repair_operations = 0
        self.n_add_remove_operations = 0
        self.n_flip_edges_operations = 0

    def get_repaired_functions(self) -> List[Function]:
        """
        Returns the list of repaired functions in the repair set.
        """
        return self.repaired_functions

    def get_flipped_edges(self) -> List[Edge]:
        """
        Returns the list of flipped edges in the repair set.
        """
        return self.flipped_edges

    def get_removed_edges(self) -> List[Edge]:
        """
        Returns the list of removed edges in the repair set.
        """
        return self.removed_edges

    def get_added_edges(self) -> List[Edge]:
        """
        Returns the list of added edges in the repair set.
        """
        return self.added_edges

    def get_n_topology_changes(self) -> int:
        """
        Returns the number of topology changes in the repair set.
        """
        return self.n_topology_changes

    def get_n_repair_operations(self) -> int:
        """
        Returns the total number of repair operations in the repair set.
        """
        return self.n_repair_operations

    def get_n_flip_edges_operations(self) -> int:
        """
        Returns the number of edge flip operations in the repair set.
        """
        return self.n_flip_edges_operations

    def get_n_add_remove_operations(self) -> int:
        """
        Returns the number of add/remove operations in the repair set.
        """
        return self.n_add_remove_operations

    def add_repaired_function(self, function: Function) -> None:
        """
        Adds a repaired function to the repair set and updates repair
        statistics.
        """
        self.repaired_functions.append(function)
        self.n_repair_operations += 1

    def add_flipped_edge(self, edge: Edge) -> None:
        """
        Adds a flipped edge to the repair set and updates repair statistics.
        """
        self.flipped_edges.append(edge)
        self.n_repair_operations += 1
        self.n_topology_changes += 1
        self.n_flip_edges_operations += 1

    def remove_edge(self, edge: Edge) -> None:
        """
        Adds a removed edge to the repair set and updates repair statistics.
        """
        self.removed_edges.append(edge)
        self.n_repair_operations += 1
        self.n_topology_changes += 1
        self.n_add_remove_operations += 1

    def add_edge(self, edge: Edge) -> None:
        """
        Adds an added edge to the repair set and updates repair statistics.
        """
        self.added_edges.append(edge)
        self.n_repair_operations += 1
        self.n_topology_changes += 1
        self.n_add_remove_operations += 1

    def is_equal(self, repair_set) -> bool:
        """
        Checks if this repair set is equal to another repair set.
        """
        # if (self.n_topology_changes != repair_set.get_n_topology_changes() or
        #         self.n_repair_operations !=
        #         repair_set.get_n_repair_operations() or
        #         self.n_flip_edges_operations !=
        #         repair_set.get_n_flip_edges_operations() or
        #         self.n_add_remove_operations !=
        #         repair_set.get_n_add_remove_operations() or
        #         len(self.repaired_functions) !=
        #         len(repair_set.get_repaired_functions()) or
        #         len(self.flipped_edges) != len(repair_set.get_flipped_edges())
        #         or len(self.removed_edges) !=
        #         len(repair_set.get_removed_edges()) or
        #         len(self.added_edges) != len(repair_set.get_added_edges())):
        if (
            (self.n_topology_changes,
             self.n_repair_operations,
             self.n_flip_edges_operations,
             self.n_add_remove_operations,
             len(self.repaired_functions),
             len(self.flipped_edges),
             len(self.removed_edges),
             len(self.added_edges))
            !=
            (repair_set.get_n_topology_changes(),
             repair_set.get_n_repair_operations(),
             repair_set.get_n_flip_edges_operations(),
             repair_set.get_n_add_remove_operations(),
             len(repair_set.get_repaired_functions()),
             len(repair_set.get_flipped_edges()),
             len(repair_set.get_removed_edges()),
             len(repair_set.get_added_edges()))
        ):
            return False

        # Check if functions are the same
        for repaired_function in self.repaired_functions:
            found = any(repaired_function.is_equal(repaired_function_2) for
                        repaired_function_2 in
                        repair_set.get_repaired_functions())
            if not found:
                return False

        # Check if flip edge sign operations are the same
        for flipped_edge in self.flipped_edges:
            found = any(flipped_edge.is_equal(flipped_edge_2, 1) for
                        flipped_edge_2 in repair_set.get_flipped_edges())  # TODO should the sign be checked?
            if not found:
                return False

        # Check if removed edges are the same
        for removed_edge in self.removed_edges:
            found = any(removed_edge.is_equal(removed_edge_2, 1) for
                        removed_edge_2 in repair_set.get_removed_edges())  # TODO should the sign be checked?
            if not found:
                return False

        # Check if added edges are the same
        for added_edge in self.added_edges:
            found = any(added_edge.is_equal(added_edge_2, 1) for added_edge_2
                        in repair_set.get_added_edges())  # TODO should the sign be checked?
            if not found:
                return False
        return True
