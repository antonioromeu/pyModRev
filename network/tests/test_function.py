import unittest
from pyfunctionhood.function import Function as PFHFunction
from pyfunctionhood.clause import Clause as Clause
from network.function import Function

class TestFunction(unittest.TestCase):
    def setUp(self):
        # Initialize the Function object
        self.function = Function('node_1')
    
    def test_initialization(self):
        # Test if the Function initializes correctly
        self.assertEqual(self.function.get_node_id(), 'node_1')
        self.assertEqual(self.function.get_distance_from_original(), 0)
        self.assertFalse(self.function.get_son_consistent())
        self.assertEqual(self.function.get_regulators(), [])
        self.assertEqual(self.function.get_regulators_by_term(), {})

    def test_get_node_id(self):
        # Test if the node_id is returned correctly
        self.assertEqual(self.function.get_node_id(), 'node_1')
    
    def test_get_distance_from_original(self):
        # Test if the distance_from_original is returned correctly
        self.assertEqual(self.function.get_distance_from_original(), 0)
    
    def test_get_son_consistent(self):
        # Test if the son_consistent is returned correctly
        self.assertFalse(self.function.get_son_consistent())

    def test_add_regulator_to_term(self):
        # Test adding a regulator to a term
        self.function.add_regulator_to_term(1, 'reg_1')
        self.assertIn('reg_1', self.function.get_regulators())
        self.assertIn('reg_1', self.function.get_regulators_by_term()[1])
        
        # Add another regulator to a different term
        self.function.add_regulator_to_term(2, 'reg_2')
        self.assertIn('reg_2', self.function.get_regulators())
        self.assertIn('reg_2', self.function.get_regulators_by_term()[2])

        # Add an existing regulator to the same term (should not duplicate)
        self.function.add_regulator_to_term(1, 'reg_1')
        self.assertEqual(len(self.function.get_regulators_by_term()[1]), 1)
        self.assertEqual(len(self.function.get_regulators()), 2)

    # def test_is_equal(self): # TODO


    # def test_get_parents(self):
    #     parents = self.function.get_parents()
    #     self.assertEqual(len(parents), 1)
    #     self.assertEqual(parents[0].get_node(), 0)

    # def test_get_children(self):
    #     children = self.function.get_children()
    #     self.assertEqual(len(children), 1)
    #     self.assertEqual(children[0].get_node(), 2)

    # def test_get_replacements_generalize(self):
    #     replacements = self.function.get_replacements(generalize=True)
    #     self.assertEqual(len(replacements), 1)
    #     self.assertEqual(replacements[0].get_node(), 0)

    # def test_get_replacements_not_generalize(self):
    #     replacements = self.function.get_replacements(generalize=False)
    #     self.assertEqual(len(replacements), 1)
    #     self.assertEqual(replacements[0].get_node(), 2)

    # def test_add_regulator_to_term_new_regulator(self):
    #     # Test adding a new regulator to a term
    #     self.function.add_regulator_to_term(1, 'node_1')
        
    #     self.assertIn('node_1', self.function.get_regulators())
    #     self.assertIn(1, self.function.get_regulators_by_term().keys())
    #     self.assertIn('node_1', self.function.get_regulators_by_term()[1])

    # def test_add_regulator_to_term_existing_regulator(self):
    #     # Test adding an existing regulator to another term
    #     self.function.add_regulator_to_term(1, 'node_1')
    #     self.function.add_regulator_to_term(2, 'node_1')

    #     # node_1 should appear only once in the regulators list
    #     self.assertEqual(self.function.get_regulators().count('node_1'), 1)
        
    #     # node_1 should appear in both terms 1 and 2
    #     self.assertIn('node_1', self.function.get_regulators_by_term()[1])
    #     self.assertIn('node_1', self.function.get_regulators_by_term()[2])

    # def test_add_regulator_to_existing_term(self):
    #     # Test adding another regulator to an existing term
    #     self.function.add_regulator_to_term(1, 'node_1')
    #     self.function.add_regulator_to_term(1, 'node_2')

    #     self.assertIn('node_1', self.function.get_regulators_by_term()[1])
    #     self.assertIn('node_2', self.function.get_regulators_by_term()[1])
    #     self.assertEqual(self.function.get_regulators_by_term()[1], ['node_1', 'node_2'])

    # def test_add_duplicate_regulator_to_same_term(self):
    #     # Test adding the same regulator to the same term multiple times
    #     self.function.add_regulator_to_term(1, 'node_1')
    #     self.function.add_regulator_to_term(1, 'node_1')

    #     # node_1 should appear only once in the term 1 list
    #     self.assertEqual(self.function.get_regulators_by_term()[1], ['node_1'])
        
    #     # node_1 should appear only once in the overall regulators list
    #     self.assertEqual(self.function.get_regulators().count('node_1'), 1)

    # def test_pfh_function_mock(self):
    #     # Test if the PFHFunction getter works as expected
    #     self.function.pfh_function = PFHFunction()  # Mock setting the PFHFunction
    #     self.assertIsInstance(self.function.get_pfh_function(), PFHFunction)

    # def test_pfh_init(self):
    #     # Mock PFHFunction constructor
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         clauses = {Clause("101"), Clause("110")}
    #         self.function.pfh_init(3, clauses)
            
    #         # Verify that PFHFunction was initialized correctly
    #         MockPFHFunction.assert_called_once_with(3, clauses)
    #         self.assertEqual(self.function.get_pfh_function(), mock_pfh_function)
    
    # def test_pfh_from_string(self):
    #     # Mock PFHFunction's fromString method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         mock_pfh_function.fromString.return_value = MagicMock(spec=PFHFunction)
    #         result = self.function.pfh_from_string(3, "{1,2},{3}")
            
    #         # Verify that fromString was called with the correct arguments
    #         mock_pfh_function.fromString.assert_called_once_with(3, "{1,2},{3}")
    #         self.assertEqual(result, mock_pfh_function.fromString.return_value)

    # def test_pfh_clone_rm_add(self):
    #     # Mock PFHFunction's clone_rm_add method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         scRm = {Clause("101")}
    #         scAdd = {Clause("110")}
    #         mock_pfh_function.clone_rm_add.return_value = MagicMock(spec=PFHFunction)
    #         result = self.function.pfh_clone_rm_add(scRm, scAdd)
            
    #         # Verify that clone_rm_add was called with the correct arguments
    #         mock_pfh_function.clone_rm_add.assert_called_once_with(scRm, scAdd)
    #         self.assertEqual(result, mock_pfh_function.clone_rm_add.return_value)

    # def test_pfh_add_clause(self):
    #     # Mock PFHFunction's add_clause method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         clause = Clause("101")
    #         self.function.pfh_add_clause(clause)
            
    #         # Verify that add_clause was called correctly
    #         mock_pfh_function.add_clause.assert_called_once_with(clause)

    # def test_pfh_get_size(self):
    #     # Mock PFHFunction's get_size method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         mock_pfh_function.get_size.return_value = 3
    #         self.assertEqual(self.function.pfh_get_size(), 3)
    #         mock_pfh_function.get_size.assert_called_once()

    # def test_pfh_get_clauses(self):
    #     # Mock PFHFunction's get_clauses method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         clauses = {Clause("101"), Clause("110")}
    #         mock_pfh_function.get_clauses.return_value = clauses
    #         self.assertEqual(self.function.pfh_get_clauses(), clauses)
    #         mock_pfh_function.get_clauses.assert_called_once()

    # def test_pfh_is_consistent(self):
    #     # Mock PFHFunction's is_consistent method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         mock_pfh_function.is_consistent.return_value = True
    #         self.assertTrue(self.function.pfh_is_consistent())
    #         mock_pfh_function.is_consistent.assert_called_once()

    # def test_pfh_evaluate(self):
    #     # Mock PFHFunction's evaluate method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         signs = MagicMock()
    #         values = MagicMock()
    #         mock_pfh_function.evaluate.return_value = True
    #         self.assertTrue(self.function.pfh_evaluate(signs, values))
    #         mock_pfh_function.evaluate.assert_called_once_with(signs, values)

    # def test_pfh_get_level(self):
    #     # Mock PFHFunction's get_level method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         mock_pfh_function.get_level.return_value = [3, 2, 1]
    #         self.assertEqual(self.function.pfh_get_level(), [3, 2, 1])
    #         mock_pfh_function.get_level.assert_called_once()

    # def test_pfh_level_cmp(self):
    #     # Mock PFHFunction's level_cmp method
    #     with patch('PFHFunction', autospec=True) as MockPFHFunction:
    #         mock_pfh_function = MockPFHFunction.return_value
    #         other_pfh_function = MagicMock(spec=PFHFunction)
    #         mock_pfh_function.level_cmp.return_value = 1
    #         self.assertEqual(self.function.pfh_level_cmp(other_pfh_function), 1)
    #         mock_pfh_function.level_cmp.assert_called_once_with(other_pfh_function)

    # def test_pfh_is_equal(self):

if __name__ == '__main__':
    unittest.main()