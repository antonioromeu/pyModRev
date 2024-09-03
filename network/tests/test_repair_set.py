import unittest
from network.repair_set import Repair_Set
from network.function import Function
from network.edge import Edge
from network.node import Node
from pyfunctionhood.clause import Clause

class TestRepairSet(unittest.TestCase):
    def setUp(self):
        self.repair_set = Repair_Set()
        self.node1 = Node('node1')
        self.node2 = Node('node2')
        self.function1 = Function('function1')
        self.clause1 = Clause('101')
        self.clause2 = Clause('111')
        self.function1.pfh_init(3, {self.clause1, self.clause2})
        self.edge1 = Edge(self.node1, self.node2, 1)
        self.edge2 = Edge(self.node2, self.node1, 0)

    def test_initial_values(self):
        self.assertEqual(self.repair_set.get_repaired_functions(), [])
        self.assertEqual(self.repair_set.get_flipped_edges(), [])
        self.assertEqual(self.repair_set.get_removed_edges(), [])
        self.assertEqual(self.repair_set.get_added_edges(), [])
        self.assertEqual(self.repair_set.get_n_topology_changes(), 0)
        self.assertEqual(self.repair_set.get_n_repair_operations(), 0)
        self.assertEqual(self.repair_set.get_n_flip_edges_operations(), 0)
        self.assertEqual(self.repair_set.get_n_add_remove_operations(), 0)

    def test_add_repaired_function(self):
        self.repair_set.add_repaired_function(self.function1)
        self.assertIn(self.function1, self.repair_set.get_repaired_functions())
        self.assertEqual(self.repair_set.get_n_repair_operations(), 1)

    def test_add_flipped_edge(self):
        self.repair_set.add_flipped_edge(self.edge1)
        self.assertIn(self.edge1, self.repair_set.get_flipped_edges())
        self.assertEqual(self.repair_set.get_n_repair_operations(), 1)
        self.assertEqual(self.repair_set.get_n_topology_changes(), 1)
        self.assertEqual(self.repair_set.get_n_flip_edges_operations(), 1)

    def test_remove_edge(self):
        self.repair_set.remove_edge(self.edge1)
        self.assertIn(self.edge1, self.repair_set.get_removed_edges())
        self.assertEqual(self.repair_set.get_n_repair_operations(), 1)
        self.assertEqual(self.repair_set.get_n_topology_changes(), 1)
        self.assertEqual(self.repair_set.get_n_add_remove_operations(), 1)

    def test_add_edge(self):
        self.repair_set.add_edge(self.edge1)
        self.assertIn(self.edge1, self.repair_set.get_added_edges())
        self.assertEqual(self.repair_set.get_n_repair_operations(), 1)
        self.assertEqual(self.repair_set.get_n_topology_changes(), 1)
        self.assertEqual(self.repair_set.get_n_add_remove_operations(), 1)

    def test_is_equal(self):
        repair_set2 = Repair_Set()

        self.repair_set.add_repaired_function(self.function1)
        self.repair_set.add_flipped_edge(self.edge1)
        self.repair_set.remove_edge(self.edge2)
        self.repair_set.add_edge(self.edge1)

        repair_set2.add_repaired_function(self.function1)
        repair_set2.add_flipped_edge(self.edge1)
        repair_set2.remove_edge(self.edge2)
        repair_set2.add_edge(self.edge1)

        self.assertTrue(self.repair_set.is_equal(repair_set2))

        repair_set2.add_edge(Edge(self.node2, self.node1, 1))
        self.assertFalse(self.repair_set.is_equal(repair_set2))

if __name__ == '__main__':
    unittest.main()