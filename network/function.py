class Function:
    def __init__(self, node=None, function=None):
        if node is not None:
            self.boolean_function = BooleanFunction.Function(node)
        else:
            self.boolean_function = function
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