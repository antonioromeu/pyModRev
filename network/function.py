from bitarray import bitarray
from pyfunctionhood.function import Function as PFHFunction
from pyfunctionhood.clause import Clause
from pyfunctionhood.hassediagram import HasseDiagram
from typing import Set, Dict, List, Tuple

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
        if self.pfh_function is None:
            return 0
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
    
    def print_level(self):
        print(self.get_level())
    
    def set_distance_from_original(self, new_distance: int) -> None:
        self.distance_from_original = new_distance
    
    def is_equal(self, other) -> bool:
        return self.get_pfh_function() == other.get_pfh_function()
    
    def compare_level(self, other) -> int:
        return self.pfh_level_cmp(other.get_pfh_function())
    
    def get_level(self) -> int:
        return self.pfh_get_level()
    
    def add_clause(self, clause: Clause) -> None:
        self.pfh_function.pfh_add_clause(clause)
    
    def add_pfh_function(self, function: PFHFunction) -> None:
        self.pfh_function = function
    
    def create_pfh_function(self) -> None:
        n_vars = len(self.regulators)
        clauses = self.create_bitarrays()
        initialised_clauses = set()
        for clause in clauses:
            initialised_clause = Clause(clause, len(clause))
            initialised_clauses.add(initialised_clause)
        self.pfh_init(n_vars, initialised_clauses)

    def create_bitarrays(self) -> List:
        # Create an empty list to store bitarrays for each clause
        clause_bitarrays = []
        
        # Iterate over each clause
        for clause_id, clause_regulators in self.regulators_by_term.items():
            # Create a bitarray initialized to 0 with a length equal to the number of regulators
            bit_arr = bitarray(len(self.regulators))
            bit_arr.setall(0)  # Initialize all bits to 0
            
            # For each regulator in the clause, set the corresponding index to 1
            for regulator in clause_regulators:
                if regulator in self.regulators:
                    idx = self.regulators.index(regulator)
                    bit_arr[idx] = 1
            
            # Append the bitarray to the list
            clause_bitarrays.append(bit_arr)
        
        # for i, b in enumerate(clause_bitarrays):
        #     print(f"Clause {i+1}: {b}")
        return clause_bitarrays
    
    def bitarray_to_regulators(self, clause) -> List[str]:
        # Create a list to store the regulators present in the clause
        present_regulators = []
        
        # Iterate over the bitarray and the corresponding regulators
        for idx, bit in enumerate(clause):
            if bit == 1:
                present_regulators.append(self.regulators[idx])
        
        return present_regulators
    
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

    # TODO should it receive another Function or a PFH Function? should there be more comparison in place? or comparing just the pfh functions is enough?
    # def is_equal(self, function: Function) -> bool:
    #     return self.pfh_function == function.get_pfh_function()
    
    # def pfh_is_equal(self, other: PFHFunction) -> bool:
    #     return self.pfh_function == other
    
    def pfh_get_replacements(self, generalize: bool) -> List:
        if generalize:
            return self.pfh_get_parents()
        return self.pfh_get_children()

    def pfh_get_parents(self) -> Tuple[Set[PFHFunction], Set[PFHFunction], Set[PFHFunction]]:
        hd = HasseDiagram(self.pfh_function.get_size())
        s1, s2, s3 = hd.get_f_parents(self.pfh_function)
        parents = s1.union(s2.union(s3))
        result = []
        for parent in parents:
            function = Function(self.get_node_id()) # TODO can/should clone_rm_add be used here?
            function.add_pfh_function(parent)
            function.set_distance_from_original(self.distance_from_original + 1)
            result.append(function)
        return result

    def pfh_get_children(self) -> Tuple[Set[PFHFunction], Set[PFHFunction], Set[PFHFunction]]:
        hd = HasseDiagram(self.pfh_function.get_size())
        s1, s2, s3 = hd.get_f_children(self.pfh_function)
        children = s1.union(s2.union(s3))
        result = []
        for child in children:
            function = Function(self.get_node_id()) # TODO can/should clone_rm_add be used here?
            function.add_pfh_function(child)
            function.set_distance_from_original(self.distance_from_original + 1)
            result.append(function)
        return result