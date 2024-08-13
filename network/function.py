import unittest
from pyfunctionhood.function import Function as PFHFunction
from pyfunctionhood.clause import Clause
from typing import Set, Dict, List
import bitarray

class Function:
    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.distance_from_original = 0 # TODO what is this?
        self.son_consistent = False # TODO what is this?
        self.pfh_function = None
        self.regulators = [] # ['node_1', 'node_2', 'node_3']
        self.regulators_by_term = {} # {1: ['node_1', 'node_2'], 2: ['node_1', 'node_3'], 3: ['node_3']}

    def get_node_id(self) -> str:
        return self.node_id
    
    def get_distance_from_original(self) -> int:
        return self.distance_from_original
    
    def get_son_consistent(self) -> bool:
        return self.son_consistent
    
    def get_pfh_function(self) -> PFHFunction:
        return self.pfh_function
    
    def get_regulators(self) -> List[str]:
        return self.regulators
    
    def get_regulators_by_term(self) -> Dict[int, List[str]]:
        return self.regulators_by_term

    def add_regulator_to_term(self, term_id: int, regulator: str) -> None:
        if regulator not in self.regulators:
            self.regulators.append(regulator)
        if term_id not in self.regulators_by_term.keys():
            self.regulators_by_term[term_id] = [regulator]
        else:
            self.regulators_by_term[term_id].append(regulator)
    
    ##### PFH section #####
    
    def pfh_init(self, n_vars: int, clauses: Set[Clause]) -> None:
        self.pfh_function = PFHFunction(n_vars, clauses)
    
    def pfh_from_string(self, nvars: int, strClauses: str) -> PFHFunction:
        return self.pfh_function.fromString(nvars, strClauses)

    def pfh_clone_rm_add(self, scRm: Set[Clause], scAdd: Set[Clause]) -> PFHFunction:
        return self.pfh_function.clone_rm_add(scRm, scAdd)

    def pfh_add_clause(self, c: Clause) -> None:
        self.pfh_function.add_clause(c)
    
    def pfh_get_size(self) -> int:
        return self.pfh_function.get_size()

    def pfh_get_clauses(self) -> Set[Clause]:
        return self.pfh_function.get_clauses()

    def pfh_is_consistent(self) -> bool:
        return self.pfh_function.is_consistent()

    def pfh_update_consistency(self) -> None:
        self.pfh_function.update_consistency()
    
    def pfh_is_independent(self) -> bool:
        return self.pfh_function.is_independent()

    def pfh_is_cover(self) -> bool:
        return self.pfh_function.is_cover()

    def pfh_evaluate(self, signs: bitarray, values: bitarray) -> bool:
        return self.pfh_function.evaluate(signs, values)

    def pfh_get_level(self) -> list[int]:
        return self.pfh_function.get_level()
    
    def pfh_level_cmp(self, other: PFHFunction) -> int:
        return self.pfh_function.level_cmp(other)
    
    # def add_element_clause(self, clause: Clause) -> None:
    #     self.pfh_function.add_clause(clause)
    
    # def add_variable_to_term(self, term_id: int, variable: str) -> None:
    #     if term_id in self.variable_map_by_id.keys():
    #         self.variable_map_by_id[term_id].append(variable)
    #     else:
    #         self.n_terms += 1 # could just be len(variable_map_by_id.keys())
    #         self.variable_map_by_id[term_id] = [variable]

    # def get_pfh_function(self) -> PFHFunction:
    #     return self.pfh_function

    # def get_number_of_regulators(self) -> int:
    #     return self.pfh_function.get_size()

    # def get_clauses(self):
    #     return self.boolean_function.get_terms()

    # def get_n_clauses(self):
    #     return self.boolean_function.get_n_terms()
    
    # def get_n_clauses(self) -> int:
    #     return len(self.pfh_function.get_clauses())

    # def print_function(self) -> None:
    #     print(self.pfh_function)

    # def is_equal(self, function):
    #     return self.boolean_function.is_equal(function.get_boolean_function())

    # def is_equal(self, function: Function) -> bool: # FIXME should it receive another Function or a PFH Function?
        # return self.pfh_function == function.get_pfh_function()
    
    # def is_equal(self, function: Function) -> bool: # FIXME should there be more comparison in place? or comparing just the pfh functions is enough?
    #     return self.pfh_function == function.get_pfh_function()

    # def get_full_level(self): # level implemented on PFH side
    #     return self.boolean_function.get_level()

    # def compare_level(self, other_level): # level implemented on PFH side
    #     return self.boolean_function.compare_level(other_level)

    # def print_function_full_level(self):
    #     print(self.boolean_function)

    # def get_parents(self): # FIXME do we need to initialise the Hasse Diagram?
    #     result = []
    #     parents = self.boolean_function.get_parents()
    #     for parent in parents:
    #         function = Function(function=parent)
    #         function.distance_from_original = self.distance_from_original + 1
    #         result.append(function)
    #     return result

    # def get_children(self): # FIXME do we need to initialise the Hasse Diagram?
    #     result = []
    #     children = self.boolean_function.get_children()
    #     for child in children:
    #         function = Function(function=child)
    #         function.distance_from_original = self.distance_from_original + 1
    #         result.append(function)
    #     return result

    # def get_replacements(self, generalize):
    #     if generalize:
    #         return self.get_parents()
    #     return self.get_children()

# class TestFunction(unittest.TestCase):
#     def setUp(self):
#         self.function = Function(4, {Clause(1110), Clause(1011), Clause(0111)})
#         self.other_function = Function(4, {Clause(1010), Clause(0110), Clause(1111)})

#     def test_initialization_with_node(self):
#         self.assertEqual(self.function.get_node(), 1)

#     def test_initialization_with_function(self):
#         boolean_function = PFHFunction(3)
#         func = Function(function=boolean_function)
#         self.assertEqual(func.get_node(), 3)

#     def test_add_element_clause(self):
#         # No assertion needed as add_variable_to_term is a stub
#         self.function.add_element_clause(1, 2)

#     def test_get_number_of_regulators(self):
#         self.assertEqual(self.function.get_number_of_regulators(), 1)

#     def test_get_regulators_map(self):
#         self.assertEqual(self.function.get_regulators_map(), {1: [1]})

#     def test_get_clauses(self):
#         self.assertEqual(self.function.get_clauses(), [(1,)])

#     def test_get_n_clauses(self):
#         self.assertEqual(self.function.get_n_clauses(), 1)

#     def test_print_function(self):
#         self.assertEqual(self.function.print_function(), "Function of node 1")

#     def test_is_equal(self):
#         func_same = Function(node=1)
#         self.assertTrue(self.function.is_equal(func_same))
#         self.assertFalse(self.function.is_equal(self.other_function))

#     def test_get_full_level(self):
#         self.assertEqual(self.function.get_full_level(), 0)

#     def test_compare_level(self):
#         self.assertEqual(self.function.compare_level(0), 0)

#     def test_print_function_full_level(self):
#         self.assertEqual(self.function.print_function_full_level(), "Function level of node 1")

#     def test_get_parents(self):
#         parents = self.function.get_parents()
#         self.assertEqual(len(parents), 1)
#         self.assertEqual(parents[0].get_node(), 0)

#     def test_get_children(self):
#         children = self.function.get_children()
#         self.assertEqual(len(children), 1)
#         self.assertEqual(children[0].get_node(), 2)

#     def test_get_replacements_generalize(self):
#         replacements = self.function.get_replacements(generalize=True)
#         self.assertEqual(len(replacements), 1)
#         self.assertEqual(replacements[0].get_node(), 0)

#     def test_get_replacements_not_generalize(self):
#         replacements = self.function.get_replacements(generalize=False)
#         self.assertEqual(len(replacements), 1)
#         self.assertEqual(replacements[0].get_node(), 2)

if __name__ == '__main__':
    unittest.main()