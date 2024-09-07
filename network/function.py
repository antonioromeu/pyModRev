import bitarray
from pyfunctionhood.function import Function as PFHFunction
from pyfunctionhood.clause import Clause
from typing import Set, Dict, List

class Function:
    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.distance_from_original = 0 # Distance between son/father of the original function in absilute value
        self.son_consistent = False # Function already found a consistent son (no need to expand further)
        self.regulators = [] # ['node_1', 'node_2', 'node_3']
        self.regulators_by_term = {} # {1: ['node_1', 'node_2'], 2: ['node_1', 'node_3'], 3: ['node_3']}
        self.pfh_function = None

    def get_node_id(self) -> str:
        return self.node_id
    
    def get_distance_from_original(self) -> int:
        return self.distance_from_original
    
    def get_son_consistent(self) -> bool:
        return self.son_consistent
    
    def get_pfh_function(self) -> PFHFunction:
        return self.pfh_function
    
    def get_clauses(self) -> Set[Clause]:
        return self.pfh_get_clauses()
    
    def get_n_clauses(self) -> int:
        return self.pfh_get_n_clauses()
    
    def get_regulators(self) -> List[str]:
        return self.regulators

    def get_n_regulators(self) -> int:
        return len(self.regulators)
    
    def get_regulators_by_term(self) -> Dict[int, List[str]]:
        return self.regulators_by_term

    def add_regulator_to_term(self, term_id: int, regulator: str) -> None:
        if regulator not in self.regulators:
            self.regulators.append(regulator)
        if term_id not in self.regulators_by_term.keys():
            self.regulators_by_term[term_id] = [regulator]
        elif regulator not in self.regulators_by_term[term_id]:
            self.regulators_by_term[term_id].append(regulator)
    
    def print_function(self) -> None:
        print(self.pfh_function)

    # def print_function_full_level(self):
    #     print(self.boolean_function)
    
    def is_equal(self, other) -> bool:
        return self.get_pfh_function() == other.get_pfh_function()
    
    def compare_level(self, other) -> int:
        return self.pfh_level_cmp(other.get_pfh_function())
    
    def add_clause(self, clause: Clause) -> None:
        self.pfh_function.add_clause(clause)
    
    # def pfh_is_equal(self, other: PFHFunction) -> bool:
    #     return self.pfh_function == other
    
    ##### pyfunctionhood wrapper #####
    
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
    
    def pfh_get_n_clauses(self) -> int:
        return len(self.pfh_function.get_clauses())

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

    def pfh_get_level(self) -> List[int]:
        return self.pfh_function.get_level()
    
    def pfh_level_cmp(self, other: PFHFunction) -> int:
        return self.pfh_function.level_cmp(other)

    # def is_equal(self, function: Function) -> bool: # TODO should it receive another Function or a PFH Function? should there be more comparison in place? or comparing just the pfh functions is enough?
        # return self.pfh_function == function.get_pfh_function()

    # def get_parents(self): # TODO do we need to initialise the Hasse Diagram?
    #     result = []
    #     parents = self.boolean_function.get_parents()
    #     for parent in parents:
    #         function = Function(function=parent)
    #         function.distance_from_original = self.distance_from_original + 1
    #         result.append(function)
    #     return result

    # def get_children(self): # TODO do we need to initialise the Hasse Diagram?
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