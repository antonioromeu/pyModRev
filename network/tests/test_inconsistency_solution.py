import unittest
from network.inconsistency_solution import Inconsistency_Solution
from network.repair_set import Repair_Set

class TestInconsistencySolution(unittest.TestCase):
    def setUp(self):
        self.solution = Inconsistency_Solution()

    def test_initial_values(self):
        self.assertEqual(self.solution.get_i_nodes(), {})
        self.assertEqual(self.solution.get_v_label(), {})
        self.assertEqual(self.solution.get_updates(), {})
        self.assertEqual(self.solution.get_i_profiles(), {})
        self.assertEqual(self.solution.get_i_nodes_profiles(), [])
        self.assertEqual(self.solution.get_n_topology_changes(), 0)
        self.assertEqual(self.solution.get_n_ar_operations(), 0)
        self.assertEqual(self.solution.get_n_e_operations(), 0)
        self.assertEqual(self.solution.get_n_repair_operations(), 0)
        self.assertFalse(self.solution.get_has_impossibility())

    def test_add_generalization(self):
        self.solution.add_generalization(1)
        self.assertIn(1, self.solution.get_i_nodes())
        self.assertTrue(self.solution.get_i_node(1).is_generalization)
        self.assertEqual(self.solution.get_i_node(1).get_repair_type(), 1)

    def test_add_particularization(self):
        self.solution.add_particularization(1)
        self.assertIn(1, self.solution.get_i_nodes())
        self.assertFalse(self.solution.get_i_node(1).is_generalization)
        self.assertEqual(self.solution.get_i_node(1).get_repair_type(), 2)

    def test_add_topological_error(self):
        self.solution.add_topological_error(1)
        self.assertIn(1, self.solution.get_i_nodes())
        self.assertTrue(self.solution.get_i_node(1).topological_error)

    def test_add_v_label(self):
        self.solution.add_v_label("profile1", 1, "value1", "time1")
        self.assertIn("profile1", self.solution.get_v_label())
        self.assertIn("time1", self.solution.get_v_label()["profile1"])
        self.assertIn(1, self.solution.get_v_label()["profile1"]["time1"])
        self.assertEqual(self.solution.get_v_label()["profile1"]["time1"][1], "value1")

    def test_add_update(self):
        self.solution.add_update("time1", "profile1", 1)
        self.assertIn("time1", self.solution.get_updates())
        self.assertIn("profile1", self.solution.get_updates()["time1"])
        self.assertIn(1, self.solution.get_updates()["time1"]["profile1"])

    def test_add_inconsistent_profile(self):
        self.solution.add_inconsistent_profile("profile1", 1)
        self.assertIn("profile1", self.solution.get_i_profiles())
        self.assertIn(1, self.solution.get_i_profiles()["profile1"])
        self.assertIn(1, self.solution.get_i_nodes_profiles())
        self.assertIn("profile1", self.solution.get_i_nodes_profiles()[1])

    def test_compare_repairs(self):
        other_solution = Inconsistency_Solution()
        other_solution.n_ar_operations = 5
        self.solution.n_ar_operations = 3
        self.assertEqual(self.solution.compare_repairs(other_solution), 1)

        other_solution.n_ar_operations = 3
        other_solution.n_e_operations = 5
        self.solution.n_e_operations = 3
        self.assertEqual(self.solution.compare_repairs(other_solution), 1)

        other_solution.n_e_operations = 3
        other_solution.n_repair_operations = 5
        self.solution.n_repair_operations = 3
        self.assertEqual(self.solution.compare_repairs(other_solution), 1)

        other_solution.n_repair_operations = 3
        self.assertEqual(self.solution.compare_repairs(other_solution), 0)

    def test_add_repair_set(self):
        repair_set = Repair_Set(1, 2, 3, 4)
        self.solution.add_generalization(1)
        self.solution.add_repair_set(1, repair_set)

        self.assertEqual(self.solution.get_n_topology_changes(), 1)
        self.assertEqual(self.solution.get_n_ar_operations(), 2)
        self.assertEqual(self.solution.get_n_e_operations(), 3)
        self.assertEqual(self.solution.get_n_repair_operations(), 4)

if __name__ == '__main__':
    unittest.main()