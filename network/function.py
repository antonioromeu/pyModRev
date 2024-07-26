import unittest

class Function:
    def __init__(self, node=None, function=None):
        if node is not None:
            self.boolean_function = BooleanFunction.Function(node)
        elif function is not None:
            self.boolean_function = function
        else:
            raise ValueError("Either node or function must be provided")
        self.distance_from_original = 0
        self.son_consistent = False

    def __del__(self):
        del self.boolean_function

    def get_node(self):
        return self.boolean_function.get_output_variable()

    def add_element_clause(self, id, node):
        self.boolean_function.add_variable_to_term(id, node)

    def get_number_of_regulators(self):
        return self.boolean_function.get_dimension()

    def get_regulators_map(self):
        return self.boolean_function.get_variable_map()

    def get_clauses(self):
        return self.boolean_function.get_terms()

    def get_n_clauses(self):
        return self.boolean_function.get_n_terms()

    def print_function(self):
        return BooleanFunction.PrintFunction(self.boolean_function)

    def is_equal(self, function):
        return self.boolean_function.is_equal(function.get_boolean_function())

    def get_full_level(self):
        return self.boolean_function.get_level()

    # Returns -1 if the original function is lower
    # Return 0 if the functions are the same level
    # Return 1 if the other function is lower
    def compare_level(self, function):
        return self.boolean_function.compare_level(function.get_boolean_function())

    def compare_level(self, other_level):
        return self.boolean_function.compare_level(other_level)

    def print_function_full_level(self):
        return BooleanFunction.PrintFunctionLevel(self.boolean_function)

    def get_parents(self):
        result = []
        parents = self.boolean_function.get_parents()
        for parent in parents:
            function = Function(function=parent)
            function.distance_from_original = self.distance_from_original + 1
            result.append(function)
        return result

    def get_children(self):
        result = []
        children = self.boolean_function.get_children()
        for child in children:
            function = Function(function=child)
            function.distance_from_original = self.distance_from_original + 1
            result.append(function)
        return result

    def get_replacements(self, generalize):
        if generalize:
            return self.get_parents()
        return self.get_children()

    def get_boolean_function(self):
        return self.boolean_function

class TestFunction(unittest.TestCase):
    def setUp(self):
        self.function = Function(node=1)
        self.other_function = Function(node=2)

    def test_initialization_with_node(self):
        self.assertEqual(self.function.get_node(), 1)

    def test_initialization_with_function(self):
        boolean_function = BooleanFunction.Function(3)
        func = Function(function=boolean_function)
        self.assertEqual(func.get_node(), 3)

    def test_add_element_clause(self):
        # No assertion needed as add_variable_to_term is a stub
        self.function.add_element_clause(1, 2)

    def test_get_number_of_regulators(self):
        self.assertEqual(self.function.get_number_of_regulators(), 1)

    def test_get_regulators_map(self):
        self.assertEqual(self.function.get_regulators_map(), {1: [1]})

    def test_get_clauses(self):
        self.assertEqual(self.function.get_clauses(), [(1,)])

    def test_get_n_clauses(self):
        self.assertEqual(self.function.get_n_clauses(), 1)

    def test_print_function(self):
        self.assertEqual(self.function.print_function(), "Function of node 1")

    def test_is_equal(self):
        func_same = Function(node=1)
        self.assertTrue(self.function.is_equal(func_same))
        self.assertFalse(self.function.is_equal(self.other_function))

    def test_get_full_level(self):
        self.assertEqual(self.function.get_full_level(), 0)

    def test_compare_level(self):
        self.assertEqual(self.function.compare_level(0), 0)

    def test_print_function_full_level(self):
        self.assertEqual(self.function.print_function_full_level(), "Function level of node 1")

    def test_get_parents(self):
        parents = self.function.get_parents()
        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0].get_node(), 0)

    def test_get_children(self):
        children = self.function.get_children()
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].get_node(), 2)

    def test_get_replacements_generalize(self):
        replacements = self.function.get_replacements(generalize=True)
        self.assertEqual(len(replacements), 1)
        self.assertEqual(replacements[0].get_node(), 0)

    def test_get_replacements_not_generalize(self):
        replacements = self.function.get_replacements(generalize=False)
        self.assertEqual(len(replacements), 1)
        self.assertEqual(replacements[0].get_node(), 2)

if __name__ == '__main__':
    unittest.main()