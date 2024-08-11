import unittest
from repair_set import Repair_Set

class Inconsistent_Node:
    def __init__(self, id: str, generalization: bool):
        self.id = id
        self.generalization = generalization
        self.repair_set = []
        self.n_topology_changes = 0
        self.n_repair_operations = 0
        self.n_add_remove_operations = 0
        self.n_flip_edges_operations = 0
        self.repaired = False
        self.topological_error = False
        self.repair_type = 1 if generalization else 2
    
    def get_id(self):
        return self.id

    def get_generalization(self):
        return self.generalization

    def get_repair_set(self):
        return self.repair_set

    def get_n_topology_changes(self):
        return self.n_topology_changes

    def get_n_repair_operations(self):
        return self.n_repair_operations

    def get_n_add_remove_operations(self):
        return self.n_add_remove_operations

    def get_n_flip_edges_operations(self):
        return self.n_flip_edges_operations

    def is_repaired(self):
        return self.repaired

    def has_topological_error(self):
        return self.topological_error

    def get_repair_type(self):
        return self.repair_type
    
    def set_repair_type(self, repair_type):
        self.repair_type = repair_type
    
    def set_topological_error(self, topological_error):
        self.topological_error = topological_error

    def add_repair_set(self, repair_set):
        if not self.repaired:
            self.repaired = True
            self.n_topology_changes = repair_set.get_n_topology_changes()
            self.n_repair_operations = repair_set.get_n_repair_operations()
            self.n_flip_edges_operations = repair_set.get_n_flip_edges_operations()
            self.n_add_remove_operations = repair_set.get_n_add_remove_operations()
        else:
            # If new solutions is worse, ignore
            if (repair_set.get_n_add_remove_operations() > self.n_add_remove_operations):
                return
            if (repair_set.get_n_add_remove_operations() == self.n_add_remove_operations and 
                repair_set.get_n_flip_edges_operations() > self.n_flip_edges_operations):
                return
            if (repair_set.get_n_add_remove_operations() == self.n_add_remove_operations and 
                repair_set.get_n_flip_edges_operations() == self.n_flip_edges_operations and
                repair_set.get_n_repair_operations() > self.n_repair_operations):
                return
            
            # If new solution is better, remove all others before
            # At this point we know that the new repair is at least as good as existing ones
            if repair_set.get_n_repair_operations() < self.n_repair_operations:
                self.repair_set.clear()
                self.n_topology_changes = repair_set.get_n_topology_changes()
                self.n_repair_operations = repair_set.get_n_repair_operations()
                self.n_add_remove_operations = repair_set.get_n_add_remove_operations()
                self.n_flip_edges_operations = repair_set.get_n_flip_edges_operations()

        self.repair_set.append(repair_set)

class TestInconsistentNode(unittest.TestCase):
    def setUp(self):
        self.node_generalization = Inconsistent_Node('node1', True)
        self.node_particularization = Inconsistent_Node('node2', False)

    def test_initial_values(self):
        self.assertEqual(self.node_generalization.get_id(), 'node1')
        self.assertTrue(self.node_generalization.get_generalization())
        self.assertEqual(self.node_generalization.get_repair_set(), [])
        self.assertEqual(self.node_generalization.get_n_topology_changes(), 0)
        self.assertEqual(self.node_generalization.get_n_repair_operations(), 0)
        self.assertEqual(self.node_generalization.get_n_add_remove_operations(), 0)
        self.assertEqual(self.node_generalization.get_n_flip_edges_operations(), 0)
        self.assertFalse(self.node_generalization.is_repaired())
        self.assertFalse(self.node_generalization.has_topological_error())
        self.assertEqual(self.node_generalization.get_repair_type(), 1)

        self.assertEqual(self.node_particularization.get_id(), 'node2')
        self.assertFalse(self.node_particularization.get_generalization())
        self.assertEqual(self.node_particularization.get_repair_type(), 2)

    def test_set_repair_type(self):
        self.node_generalization.set_repair_type(3)
        self.assertEqual(self.node_generalization.get_repair_type(), 3)

    def test_set_topological_error(self):
        self.node_generalization.set_topological_error(True)
        self.assertTrue(self.node_generalization.has_topological_error())

    def test_add_repair_set(self):
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