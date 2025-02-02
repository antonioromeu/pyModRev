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
        if self.regulators:
            if self.pfh_function is None:
                self.create_pfh_function()
            return self.pfh_get_n_clauses()
        else:
            return 0
    
    def get_regulators(self) -> List[str]:
        return self.regulators

    def get_n_regulators(self) -> int:
        return len(self.regulators)
    
    def get_regulators_by_term(self) -> Dict[int, List[str]]:
        return self.regulators_by_term

    def get_n_terms(self) -> int:
        return len(self.regulators_by_term)

    def add_regulator_to_term(self, term_id: int, regulator: str) -> None:
        if regulator not in self.regulators:
            self.regulators.append(regulator)
        if term_id not in self.regulators_by_term.keys():
            self.regulators_by_term[term_id] = [regulator]
        elif regulator not in self.regulators_by_term[term_id]:
            self.regulators_by_term[term_id].append(regulator)
    
    def print_function(self) -> str:
        result = ""
        if self.get_n_regulators() < 1:
            result += "Empty function"
            return result
        terms = self.get_regulators_by_term()
        for i in range(1, self.get_n_terms() + 1):
            result += "("
            term = terms[i]
            first = True
            for t in term:
                if not first:
                    result += " && "
                first = False
                result += t
            result += ")"
            if i < self.get_n_terms():
                result += " || "
        return result
    
    def print_level(self):
        print(self.get_level())
    
    def set_distance_from_original(self, new_distance: int) -> None:
        self.distance_from_original = new_distance
    
    def set_son_consistent(self, new_son_consistent: bool) -> None:
        self.son_consistent = new_son_consistent
    
    def set_regulators(self, new_regulators: List[str]) -> None:
        self.regulators = new_regulators
    
    def set_regulators_by_term(self, new_regulators_by_term: Dict[int, List[str]]) -> None:
        self.regulators_by_term = new_regulators_by_term
    
    def is_equal(self, other) -> bool:
        return self.get_pfh_function() == other.get_pfh_function()
    
    def compare_level(self, other) -> int:
        if self is not None and self.get_pfh_function() is None:
            self.create_pfh_function()
        if other is not None and other.get_pfh_function() is None and type(other) == Function:
            other.create_pfh_function()
        return self.pfh_level_cmp(other.get_pfh_function())

    def compare_level_list(self, other: List) -> int:
        return self.pfh_level_cmp_list(other)
    
    def get_level(self) -> int:
        return self.pfh_get_level()

    def get_replacements(self, generalize: bool) -> List:
        return self.pfh_get_replacements(generalize)
    
    def add_clause(self, clause: Clause) -> None:
        self.pfh_add_clause(clause)
    
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

    def create_bitarrays(self) -> Set:
        clause_bitarrays = []
        for clause_id, clause_regulators in self.regulators_by_term.items():
            bit_arr = bitarray(len(self.regulators))
            bit_arr.setall(0)
            # For each regulator in the clause, set the corresponding index to 1
            for regulator in clause_regulators:
                if regulator in self.regulators:
                    idx = self.regulators.index(regulator)
                    bit_arr[idx] = 1
            clause_bitarrays.append(bit_arr)
        return clause_bitarrays
    
    # def get_active_regulators(self, clauses):
    #     active_regulators = {}
    #     ordered_clauses = list(clauses)
    #     for term, active_indices in enumerate(ordered_clauses, start=1): # Enumerate through each term (starting from 1 for the term number)
    #         active_regulators[term] = []
    #         for term2, idx in enumerate(active_indices.get_signature(), start=0):
    #             if idx:
    #                 active_regulators[term].append(self.regulators[term2]) # Map each active index to the corresponding regulator
    #     return active_regulators
    
    def get_active_regulators(self, clauses):
        active_regulators = {}
        ordered_clauses = list(clauses)
        for term, active_indices in enumerate(ordered_clauses, start=1): # Enumerate through each term (starting from 1 for the term number)
            active_regulators[term] = self.bitarray_to_regulators(active_indices)
            # for term2, idx in enumerate(active_indices.get_signature(), start=0):
            #     if idx:
            #         active_regulators[term].append(self.regulators[term2]) # Map each active index to the corresponding regulator
        return active_regulators
    
    def bitarray_to_regulators(self, clause: Clause) -> List[str]:
        present_regulators = []
        for idx, bit in enumerate(clause.get_signature()):
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

    def pfh_level_cmp_list(self, other: List) -> int:
        return self.pfh_function.level_cmp_list(other)

    # TODO should it receive another Function or a PFH Function? should there be more comparison in place? or comparing just the pfh functions is enough?
    # def is_equal(self, function: Function) -> bool:
    #     return self.pfh_function == function.get_pfh_function()
    
    # def pfh_is_equal(self, other: PFHFunction) -> bool:
    #     return self.pfh_function == other
    
    def pfh_get_replacements(self, generalize: bool) -> List:
        if not self.pfh_function:
            self.create_pfh_function()
        if generalize:
            return self.pfh_get_parents()
        return self.pfh_get_children()

    def pfh_get_parents(self) -> List:
        hd = HasseDiagram(self.pfh_function.get_size())
        s1, s2, s3 = hd.get_f_parents(self.pfh_function)
        parents = s1.union(s2.union(s3))
        result = []
        for parent in parents: # FIXME do the setters make sense?
            function = Function(self.get_node_id())
            function.set_distance_from_original(self.get_distance_from_original() + 1)
            function.set_son_consistent(parent.is_consistent()) # FIXME does it make sense to put consistency equal to the one of the parent or should it be the equal to current function (self)?
            function.set_regulators(self.get_regulators()) # FIXME should regs be the same?
            function.set_regulators_by_term(self.get_active_regulators(parent.get_clauses()))
            function.add_pfh_function(parent)
            result.append(function)
        return result

    def pfh_get_children(self) -> List:
        hd = HasseDiagram(self.pfh_function.get_size())
        s1, s2, s3 = hd.get_f_children(self.pfh_function)
        children = s1.union(s2.union(s3))
        result = []
        for child in children: # FIXME do the setters make sense?
            function = Function(self.get_node_id()) # TODO can/should clone_rm_add be used here?
            function.set_distance_from_original(self.get_distance_from_original() + 1)
            function.set_son_consistent(child.is_consistent()) # FIXME does it make sense to put consistency equal to the one of the child or should it be the equal to current function (self)?
            function.set_regulators(self.get_regulators()) # FIXME should regs be the same?
            function.set_regulators_by_term(self.get_active_regulators(child.get_clauses()))
            function.add_pfh_function(child)
            result.append(function)
        return result