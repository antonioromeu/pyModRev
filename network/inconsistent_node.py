"""
This module defines the Inconsistent_Node class, which represents a node in a
network that is inconsistent.
The class provides methods to manage and analyze repair sets and
inconsistencies for the node.
"""

from typing import List
from network.repair_set import Repair_Set


class Inconsistent_Node:
    """
    Represents a node in a network that is inconsistent.
    Provides methods to manage repair sets, track repair operations, and
    determine if the node has been repaired.
    """
    def __init__(self, node_id: str, generalization: bool):
        """
        Initializes an inconsistent node with an identifier and a
        generalization flag.
        """
        self.id = node_id
        self.generalization = generalization
        self.repair_set = []  # List of Repair_Sets
        self.n_topology_changes = 0
        self.n_repair_operations = 0
        self.n_add_remove_operations = 0
        self.n_flip_edges_operations = 0
        self.repaired = False
        self.topological_error = False
        self.repair_type = 1 if generalization else 2

    def get_id(self) -> str:
        """
        Returns the identifier of the node.
        """
        return self.id

    def get_generalization(self) -> bool:
        """
        Returns whether the node is a generalization.
        """
        return self.generalization

    def get_repair_set(self) -> List[Repair_Set]:
        """
        Returns the list of repair sets associated with the node.
        """
        return self.repair_set

    def get_n_topology_changes(self) -> int:
        """
        Returns the number of topology changes required to repair the node.
        """
        return self.n_topology_changes

    def get_n_repair_operations(self) -> int:
        """
        Returns the number of repair operations required to repair the node.
        """
        return self.n_repair_operations

    def get_n_add_remove_operations(self) -> int:
        """
        Returns the number of add/remove operations required to repair the
        node.
        """
        return self.n_add_remove_operations

    def get_n_flip_edges_operations(self) -> int:
        """
        Returns the number of edge flip operations required to repair the node.
        """
        return self.n_flip_edges_operations

    def is_repaired(self) -> bool:
        """
        Returns whether the node has been repaired.
        """
        return self.repaired

    def has_topological_error(self) -> bool:
        """
        Returns whether the node has a topological error.
        """
        return self.topological_error

    def get_repair_type(self) -> int:
        """
        Returns the repair type of the node (1 for generalization, 2 for
        particularization).
        """
        return self.repair_type

    def set_repair_type(self, repair_type: int) -> None:
        """
        Sets the repair type of the node.
        """
        self.repair_type = repair_type

    def set_topological_error(self, topological_error: bool) -> None:
        """
        Sets whether the node has a topological error.
        """
        self.topological_error = topological_error

    def add_repair_set(self, repair_set: Repair_Set) -> None:
        """
        Adds a repair set to the node and updates repair statistics.
        If the new repair set is better than existing ones, it replaces them.
        """
        if not self.repaired:
            self.repaired = True
            self.n_topology_changes = repair_set.get_n_topology_changes()
            self.n_repair_operations = repair_set.get_n_repair_operations()
            self.n_flip_edges_operations = \
                repair_set.get_n_flip_edges_operations()
            self.n_add_remove_operations = \
                repair_set.get_n_add_remove_operations()
        else:
            # If new solutions is worse, ignore
            if (repair_set.get_n_add_remove_operations() >
                    self.n_add_remove_operations):
                return
            if (repair_set.get_n_add_remove_operations() ==
                    self.n_add_remove_operations and
                    repair_set.get_n_flip_edges_operations() >
                    self.n_flip_edges_operations):
                return
            if (repair_set.get_n_add_remove_operations() ==
                    self.n_add_remove_operations and
                    repair_set.get_n_flip_edges_operations() ==
                    self.n_flip_edges_operations and
                    repair_set.get_n_repair_operations() >
                    self.n_repair_operations):
                return

            # If new solution is better, remove all others before
            # At this point we know that the new repair is at least as good as
            # existing ones
            if repair_set.get_n_repair_operations() < self.n_repair_operations:
                self.repair_set.clear()
                self.n_topology_changes = repair_set.get_n_topology_changes()
                self.n_repair_operations = repair_set.get_n_repair_operations()
                self.n_add_remove_operations = \
                    repair_set.get_n_add_remove_operations()
                self.n_flip_edges_operations = \
                    repair_set.get_n_flip_edges_operations()
        self.repair_set.append(repair_set)
