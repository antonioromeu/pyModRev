import unittest
from network.inconsistent_node import Inconsistent_Node
from network.repair_set import Repair_Set
from network.function import Function
from network.edge import Edge
from network.node import Node
from pyfunctionhood.clause import Clause

class TestInconsistentNode(unittest.TestCase):
    def setUp(self):
        self.node_generalization = Inconsistent_Node('inconsistent_node_1', True)
        self.node_particularization = Inconsistent_Node('inconsistent_node_2', False)
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
        self.assertEqual(self.node_generalization.get_id(), 'inconsistent_node_1')
        self.assertTrue(self.node_generalization.get_generalization())
        self.assertEqual(self.node_generalization.get_repair_set(), [])
        self.assertEqual(self.node_generalization.get_n_topology_changes(), 0)
        self.assertEqual(self.node_generalization.get_n_repair_operations(), 0)
        self.assertEqual(self.node_generalization.get_n_add_remove_operations(), 0)
        self.assertEqual(self.node_generalization.get_n_flip_edges_operations(), 0)
        self.assertFalse(self.node_generalization.is_repaired())
        self.assertFalse(self.node_generalization.has_topological_error())
        self.assertEqual(self.node_generalization.get_repair_type(), 1)

        self.assertEqual(self.node_particularization.get_id(), 'inconsistent_node_2')
        self.assertFalse(self.node_particularization.get_generalization())
        self.assertEqual(self.node_particularization.get_repair_type(), 2)

    def test_set_repair_type(self):
        self.node_generalization.set_repair_type(3)
        self.assertEqual(self.node_generalization.get_repair_type(), 3)

    def test_set_topological_error(self):
        self.node_generalization.set_topological_error(True)
        self.assertTrue(self.node_generalization.has_topological_error())

    def test_add_repair_set(self):
        self.repair_set = Repair_Set()
        self.node1 = Node('node1')
        self.node2 = Node('node2')
        self.function1 = Function('function1')
        self.clause1 = Clause('101')
        self.clause2 = Clause('111')
        self.function1.pfh_init(3, {self.clause1, self.clause2})
        self.edge1 = Edge(self.node1, self.node2, 1)
        self.edge2 = Edge(self.node2, self.node1, 0)

        repair_set1 = Repair_Set(1, 2, 3, 4)
        repair_set2 = Repair_Set(1, 1, 2, 3)  # Better repair set

        self.node_generalization.add_repair_set(repair_set1)
        self.assertTrue(self.node_generalization.is_repaired())
        self.assertEqual(self.node_generalization.get_n_topology_changes(), 1)
        self.assertEqual(self.node_generalization.get_n_repair_operations(), 2)
        self.assertEqual(self.node_generalization.get_n_add_remove_operations(), 3)
        self.assertEqual(self.node_generalization.get_n_flip_edges_operations(), 4)

        self.node_generalization.add_repair_set(repair_set2)
        self.assertEqual(self.node_generalization.get_n_topology_changes(), 1)
        self.assertEqual(self.node_generalization.get_n_repair_operations(), 1)
        self.assertEqual(self.node_generalization.get_n_add_remove_operations(), 2)
        self.assertEqual(self.node_generalization.get_n_flip_edges_operations(), 3)
        self.assertEqual(len(self.node_generalization.get_repair_set()), 1)

    def test_add_worse_repair_set(self):
        repair_set1 = Repair_Set(1, 2, 3, 4)
        repair_set2 = Repair_Set(1, 3, 4, 5)  # Worse repair set

        self.node_generalization.add_repair_set(repair_set1)
        self.node_generalization.add_repair_set(repair_set2)

        self.assertEqual(self.node_generalization.get_n_topology_changes(), 1)
        self.assertEqual(self.node_generalization.get_n_repair_operations(), 2)
        self.assertEqual(self.node_generalization.get_n_add_remove_operations(), 3)
        self.assertEqual(self.node_generalization.get_n_flip_edges_operations(), 4)
        self.assertEqual(len(self.node_generalization.get_repair_set()), 1)

if __name__ == '__main__':
    unittest.main()