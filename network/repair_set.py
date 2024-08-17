import unittest
from network.edge import Edge
from network.function import Function
from typing import List

class Repair_Set:
    def __init__(self):
        self.repaired_functions = [] # List of Functions
        self.flipped_edges = [] # List of Edges
        self.removed_edges = [] # List of Edges
        self.added_edges = [] # List of Edges
        self.n_topology_changes = 0
        self.n_repair_operations = 0
        self.n_add_remove_operations = 0
        self.n_flip_edges_operations = 0
    
    def get_repaired_functions(self) -> List[Function]:
        return self.repaired_functions
    
    def get_flipped_edges(self) -> List[Edge]:
        return self.flipped_edges
    
    def get_removed_edges(self) -> List[Edge]:
        return self.removed_edges
    
    def get_added_edges(self) -> List[Edge]:
        return self.added_edges

    def get_n_topology_changes(self) -> int:
        return self.n_topology_changes

    def get_n_repair_operations(self) -> int:
        return self.n_repair_operations

    def get_n_flip_edges_operations(self) -> int:
        return self.n_flip_edges_operations

    def get_n_add_remove_operations(self) -> int:
        return self.n_add_remove_operations

    def add_repaired_function(self, function: Function) -> None:
        self.repaired_functions.append(function)
        self.n_repair_operations += 1

    def add_flipped_edge(self, edge: Edge) -> None:
        self.flipped_edges.append(edge)
        self.n_repair_operations += 1
        self.n_topology_changes += 1
        self.n_flip_edges_operations += 1

    def remove_edge(self, edge: Edge) -> None:
        self.removed_edges.append(edge)
        self.n_repair_operations += 1
        self.n_topology_changes += 1
        self.n_add_remove_operations += 1

    def add_edge(self, edge: Edge) -> None:
        self.added_edges.append(edge)
        self.n_repair_operations += 1
        self.n_topology_changes += 1
        self.n_add_remove_operations += 1

    def is_equal(self, repair_set) -> bool:
        if (self.n_topology_changes != repair_set.get_n_topology_changes() or
                self.n_repair_operations != repair_set.get_n_repair_operations() or
                self.n_flip_edges_operations != repair_set.get_n_flip_edges_operations() or
                self.n_add_remove_operations != repair_set.get_n_add_remove_operations() or
                len(self.repaired_functions) != len(repair_set.get_repaired_functions()) or
                len(self.flipped_edges) != len(repair_set.get_flipped_edges()) or
                len(self.removed_edges) != len(repair_set.get_removed_edges()) or
                len(self.added_edges) != len(repair_set.get_added_edges())):
            return False

        # Check if functions are the same
        for repaired_function in self.repaired_functions:
            found = any(repaired_function.is_equal(repaired_function_2) for repaired_function_2 in repair_set.get_repaired_functions())
            if not found:
                return False

        # Check if flip edge sign operations are the same
        for flipped_edge in self.flipped_edges:
            found = any(flipped_edge.is_equal(flipped_edge_2) for flipped_edge_2 in repair_set.get_flipped_edges())
            if not found:
                return False

        # Check if removed edges are the same
        for removed_edge in self.removed_edges:
            found = any(removed_edge.is_equal(removed_edge_2) for removed_edge_2 in repair_set.get_removed_edges())
            if not found:
                return False

        # Check if added edges are the same
        for added_edge in self.added_edges:
            found = any(added_edge.is_equal(added_edge_2) for added_edge_2 in repair_set.get_added_edges())
            if not found:
                return False
        return True

# class TestRepairSet(unittest.TestCase):
#     def setUp(self):
#         self.repair_set = Repair_Set()

#     def test_initial_values(self):
#         self.assertEqual(self.repair_set.get_repaired_functions(), [])
#         self.assertEqual(self.repair_set.get_flipped_edges(), [])
#         self.assertEqual(self.repair_set.get_removed_edges(), [])
#         self.assertEqual(self.repair_set.get_added_edges(), [])
#         self.assertEqual(self.repair_set.get_n_topology_changes(), 0)
#         self.assertEqual(self.repair_set.get_n_repair_operations(), 0)
#         self.assertEqual(self.repair_set.get_n_filp_edges_operations(), 0)
#         self.assertEqual(self.repair_set.get_n_add_remove_operations(), 0)

#     def test_add_repaired_function(self):
#         function = Function('function1')
#         self.repair_set.add_repaired_function(function)
#         self.assertIn(function, self.repair_set.get_repaired_functions())
#         self.assertEqual(self.repair_set.get_n_repair_operations(), 1)

#     def test_add_flipped_edge(self):
#         edge_instance = Edge('edge1')
#         self.repair_set.add_flipped_edge(edge_instance)
#         self.assertIn(edge_instance, self.repair_set.get_flipped_edges())
#         self.assertEqual(self.repair_set.get_n_repair_operations(), 1)
#         self.assertEqual(self.repair_set.get_n_topology_changes(), 1)
#         self.assertEqual(self.repair_set.get_n_filp_edges_operations(), 1)

#     def test_remove_edge(self):
#         edge_instance = Edge('edge1')
#         self.repair_set.remove_edge(edge_instance)
#         self.assertIn(edge_instance, self.repair_set.get_removed_edges())
#         self.assertEqual(self.repair_set.get_n_repair_operations(), 1)
#         self.assertEqual(self.repair_set.get_n_topology_changes(), 1)
#         self.assertEqual(self.repair_set.get_n_add_remove_operations(), 1)

#     def test_add_edge(self):
#         edge_instance = Edge('edge1')
#         self.repair_set.add_edge(edge_instance)
#         self.assertIn(edge_instance, self.repair_set.get_added_edges())
#         self.assertEqual(self.repair_set.get_n_repair_operations(), 1)
#         self.assertEqual(self.repair_set.get_n_topology_changes(), 1)
#         self.assertEqual(self.repair_set.get_n_add_remove_operations(), 1)

#     def test_is_equal(self):
#         repair_set1 = Repair_Set()
#         repair_set2 = Repair_Set()

#         function_instance = Function('function1')
#         edge1 = Edge('edge1')
#         edge2 = Edge('edge2')

#         repair_set1.add_repaired_function(function_instance)
#         repair_set1.add_flipped_edge(edge1)
#         repair_set1.remove_edge(edge2)
#         repair_set1.add_edge(edge1)

#         repair_set2.add_repaired_function(function_instance)
#         repair_set2.add_flipped_edge(edge1)
#         repair_set2.remove_edge(edge2)
#         repair_set2.add_edge(edge1)

#         self.assertTrue(repair_set1.is_equal(repair_set2))

#         repair_set2.add_edge(Edge('edge3'))
#         self.assertFalse(repair_set1.is_equal(repair_set2))

# if __name__ == '__main__':
#     unittest.main()