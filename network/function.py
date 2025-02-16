"""
This module provides a comprehensive implementation for representing and
managing Boolean functions within regulatory networks. It integrates with the
PyFunctionhood library to enable advanced operations on function structures
including clause management, Hasse diagram navigation, and consistency
analysis.
"""

from typing import Set, Dict, List
from bitarray import bitarray
from pyfunctionhood.function import Function as PFHFunction
from pyfunctionhood.clause import Clause
from pyfunctionhood.hassediagram import HasseDiagram


class Function:
    """
    Represents a Boolean function in a network, including its regulators,
    clauses, and consistency properties. This class provides methods for
    managing the function's structure and interfacing with the PyFunctionhood
    library.
    """
    def __init__(self, node_id: str) -> None:
        """
        Initializes a Function object with a given node ID.
        """
        self.node_id = node_id
        # Distance between son/father of the original function in absolute
        # value
        self.distance_from_original = 0
        # Function already found a consistent son (no need to expand further)
        self.son_consistent = False
        # ['node_1', 'node_2', 'node_3']
        self.regulators = []
        # {1: ['node_1', 'node_2'], 2: ['node_1', 'node_3'], 3: ['node_3']}
        self.regulators_by_term = {}
        self.pfh_function = None

    def get_node_id(self) -> str:
        """
        Returns the node ID of the function.
        """
        return self.node_id

    def get_distance_from_original(self) -> int:
        """
        Returns the distance of this function from the original function.
        """
        return self.distance_from_original

    def get_son_consistent(self) -> bool:
        """
        Returns whether this function has a consistent descendant.
        """
        return self.son_consistent

    def get_pfh_function(self) -> PFHFunction:
        """
        Returns the PyFunctionhood function representation.
        """
        return self.pfh_function

    def get_clauses(self) -> Set[Clause]:
        """
        Returns the set of clauses in the function.
        """
        return self.pfh_get_clauses()

    def get_n_clauses(self) -> int:
        """
        Returns the number of clauses in the function.
        """
        if self.regulators:
            if self.pfh_function is None:
                self.create_pfh_function()
            return self.pfh_get_n_clauses()
        return 0

    def get_regulators(self) -> List[str]:
        """
        Returns the list of regulators for this function.
        """
        return self.regulators

    def get_n_regulators(self) -> int:
        """
        Returns the number of regulators in the function.
        """
        return len(self.regulators)

    def get_regulators_by_term(self) -> Dict[int, List[str]]:
        """
        Returns a dictionary mapping terms to their respective regulators.
        """
        return self.regulators_by_term

    def get_n_terms(self) -> int:
        """
        Returns the number of terms in the function.
        """
        return len(self.regulators_by_term)

    def add_regulator_to_term(self, term_id: int, regulator: str) -> None:
        """
        Adds a regulator to a specific term in the function.
        """
        if regulator not in self.regulators:
            self.regulators.append(regulator)
        if term_id not in self.regulators_by_term.keys():
            self.regulators_by_term[term_id] = [regulator]
        elif regulator not in self.regulators_by_term[term_id]:
            self.regulators_by_term[term_id].append(regulator)

    def print_function(self) -> str:
        """
        Returns a string representation of the function.
        """
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
        """
        Prints the function's hierarchical level in the Hasse diagram.
        """
        print(self.get_level())

    def set_distance_from_original(self, new_distance: int) -> None:
        """
        Sets the distance from the original function.
        """
        self.distance_from_original = new_distance

    def set_son_consistent(self, new_son_consistent: bool) -> None:
        """
        Marks whether the function has found a consistent descendant.
        """
        self.son_consistent = new_son_consistent

    def set_regulators(self, new_regulators: List[str]) -> None:
        """
        Sets the list of regulatory nodes for this function.
        """
        self.regulators = new_regulators

    def set_regulators_by_term(self,
                               new_regulators_by_term: Dict[int, List[str]]) \
            -> None:
        """
        Assigns regulators to specific terms in the function.
        """
        self.regulators_by_term = new_regulators_by_term

    def is_equal(self, other) -> bool:
        """
        Compares this function with another function for equality.
        """
        return self.get_pfh_function() == other.get_pfh_function()

    def compare_level(self, other) -> int:
        """
        Compares the hierarchical level of this function with another function.
        """
        if self is not None and self.get_pfh_function() is None:
            self.create_pfh_function()
        if other is not None and other.get_pfh_function() is None \
                and isinstance(other, Function):
            other.create_pfh_function()
        return self.pfh_level_cmp(other.get_pfh_function())

    def compare_level_list(self, other: List) -> int:
        """
        Compares the function's hierarchical level with a list of levels.
        """
        return self.pfh_level_cmp_list(other)

    def get_level(self) -> int:
        """
        Returns the hierarchical level of this function.
        """
        return self.pfh_get_level()

    def get_replacements(self, generalize: bool) -> List:
        """
        Returns a list of replacement functions, either generalizing or
        specializing.
        """
        return self.pfh_get_replacements(generalize)

    def add_clause(self, clause: Clause) -> None:
        """
        Adds a clause to the function.
        """
        self.pfh_add_clause(clause)

    def add_pfh_function(self, function: PFHFunction) -> None:
        """
        Sets the PyFunctionhood function representation for this function.
        """
        self.pfh_function = function

    def create_pfh_function(self) -> None:
        """
        Initializes the PyFunctionhood function based on stored clauses.
        """
        n_vars = len(self.regulators)
        clauses = self.create_bitarrays()
        initialised_clauses = set()
        for clause in clauses:
            initialised_clause = Clause(clause, len(clause))
            initialised_clauses.add(initialised_clause)
        self.pfh_init(n_vars, initialised_clauses)

    def create_bitarrays(self) -> Set:
        """
        Creates bitarray representations of the function's clauses.
        """
        clause_bitarrays = []
        for _, clause_regulators in self.regulators_by_term.items():
            bit_arr = bitarray(len(self.regulators))
            bit_arr.setall(0)
            # For each regulator in the clause, set the corresponding index to
            # 1
            for regulator in clause_regulators:
                if regulator in self.regulators:
                    idx = self.regulators.index(regulator)
                    bit_arr[idx] = 1
            clause_bitarrays.append(bit_arr)
        return clause_bitarrays

    def get_active_regulators(self, clauses):
        """
        Retrieves active regulators for each clause in the given set.
        """
        active_regulators = {}
        ordered_clauses = list(clauses)
        # Enumerate through each term (starting from 1 for the term number)
        for term, active_indices in enumerate(ordered_clauses, start=1):
            active_regulators[term] = self.bitarray_to_regulators(
                active_indices)
        return active_regulators

    def bitarray_to_regulators(self, clause: Clause) -> List[str]:
        """
        Converts a clause's bitarray representation into a list of regulators.
        """
        return [self.regulators[idx] for idx, bit
                in enumerate(clause.get_signature()) if bit == 1]

    # pyfunctionhood wrapper

    def pfh_init(self, n_vars: int, clauses: Set[Clause]) -> None:
        """
        Initializes the PFH function with the given number of variables and
        clauses.
        """
        self.pfh_function = PFHFunction(n_vars, clauses)

    def pfh_from_string(self, nvars: int, str_clauses: str) -> PFHFunction:
        """
        Creates a PFH function from a string representation of clauses.
        """
        return self.pfh_function.fromString(nvars, str_clauses)

    def pfh_clone_rm_add(self, sc_rm: Set[Clause], sc_add: Set[Clause]) \
            -> PFHFunction:
        """
        Creates a clone of the current PFH function, removing and adding
        specified clauses.
        """
        return self.pfh_function.clone_rm_add(sc_rm, sc_add)

    def pfh_add_clause(self, c: Clause) -> None:
        """
        Adds a clause to the PFH function.
        """
        self.pfh_function.add_clause(c)

    def pfh_get_size(self) -> int:
        """
        Gets the number of clauses in the PFH function.
        """
        return self.pfh_function.get_size()

    def pfh_get_clauses(self) -> Set[Clause]:
        """
        Retrieves the set of clauses in the PFH function.
        """
        return self.pfh_function.get_clauses()

    def pfh_get_n_clauses(self) -> int:
        """
        Gets the number of clauses in the PFH function.
        """
        return len(self.pfh_function.get_clauses())

    def pfh_is_consistent(self) -> bool:
        """
        Checks if the PFH function is consistent.
        """
        return self.pfh_function.is_consistent()

    def pfh_update_consistency(self) -> None:
        """
        Updates the consistency status of the PFH function.
        """
        self.pfh_function.update_consistency()

    def pfh_is_independent(self) -> bool:
        """
        Checks if the PFH function is independent.
        """
        return self.pfh_function.is_independent()

    def pfh_is_cover(self) -> bool:
        """
        Checks if the PFH function is a cover function.
        """
        return self.pfh_function.is_cover()

    def pfh_evaluate(self, signs: bitarray, values: bitarray) -> bool:
        """
        Evaluates the PFH function using given sign and value bitarrays.
        """
        return self.pfh_function.evaluate(signs, values)

    def pfh_get_level(self) -> List[int]:
        """
        Gets the level representation of the PFH function.
        """
        return self.pfh_function.get_level()

    def pfh_level_cmp(self, other: PFHFunction) -> int:
        """
        Compares the level of this PFH function with another.
        """
        return self.pfh_function.level_cmp(other)

    def pfh_level_cmp_list(self, other: List) -> int:
        """
        Compares the level of this PFH function against a list of other
        functions.
        """
        return self.pfh_function.level_cmp_list(other)

    def pfh_get_replacements(self, generalize: bool) -> List:
        """
        Gets replacement functions by generalizing or specializing.
        """
        if not self.pfh_function:
            self.create_pfh_function()
        return self.pfh_get_parents() if generalize \
            else self.pfh_get_children()

    # def pfh_get_parents(self) -> List:
    #     """
    #     Gets the parent functions in the Hasse diagram.
    #     """
    #     hd = HasseDiagram(self.pfh_function.get_size())
    #     s1, s2, s3 = hd.get_f_parents(self.pfh_function)
    #     parents = s1.union(s2.union(s3))
    #     result = []
    #     # FIXME do the setters make sense?
    #     for parent in parents:
    #         function = Function(self.get_node_id())
    #         function.set_distance_from_original(
    #             self.get_distance_from_original() + 1)
    #         # FIXME does it make sense to put consistency equal to the one of
    #         # the parent or should it be the equal to current function (self)?
    #         function.set_son_consistent(parent.is_consistent())
    #         # FIXME should regs be the same?
    #         function.set_regulators(self.get_regulators())
    #         function.set_regulators_by_term(self.get_active_regulators(
    #             parent.get_clauses()))
    #         function.add_pfh_function(parent)
    #         result.append(function)
    #     return result

    # def pfh_get_children(self) -> List:
    #     """
    #     Gets the child functions in the Hasse diagram.
    #     """
    #     hd = HasseDiagram(self.pfh_function.get_size())
    #     s1, s2, s3 = hd.get_f_children(self.pfh_function)
    #     children = s1.union(s2.union(s3))
    #     result = []
    #     # FIXME do the setters make sense?
    #     for child in children:
    #         # TODO can/should clone_rm_add be used here?
    #         function = Function(self.get_node_id())
    #         function.set_distance_from_original(
    #             self.get_distance_from_original() + 1)
    #         # FIXME does it make sense to put consistency equal to the one of
    #         # the child or should it be the equal to current function (self)?
    #         function.set_son_consistent(child.is_consistent())
    #         # FIXME should regs be the same?
    #         function.set_regulators(self.get_regulators())
    #         function.set_regulators_by_term(self.get_active_regulators(
    #             child.get_clauses()))
    #         function.add_pfh_function(child)
    #         result.append(function)
    #     return result

    def get_hasse_relationships(self, relationship_type: str) -> List:
        """
        Helper function to get parent/child relationships from Hasse diagram.
        """
        hd = HasseDiagram(self.pfh_function.get_size())

        # Get the appropriate method based on relationship type
        get_method = {
            'parents': hd.get_f_parents,
            'children': hd.get_f_children
        }[relationship_type]

        # Get and combine sets
        s1, s2, s3 = get_method(self.pfh_function)
        return s1 | s2 | s3  # Using set union operator

    def create_function_from_element(self, element):
        """
        Create and configure a new Function instance from Hasse element.
        """
        new_func = Function(self.get_node_id())
        new_func.set_distance_from_original(
            self.get_distance_from_original() + 1)
        new_func.set_son_consistent(element.is_consistent())
        new_func.set_regulators(self.get_regulators())

        # Get clauses based on relationship type
        clauses = element.get_clauses()
        new_func.set_regulators_by_term(self.get_active_regulators(clauses))
        new_func.add_pfh_function(element)
        return new_func

    def pfh_get_parents(self) -> List:
        """
        Get parent functions in the Hasse diagram.
        """
        return [
            self.create_function_from_element(parent)
            for parent in self.get_hasse_relationships('parents')
        ]

    def pfh_get_children(self) -> List:
        """
        Get child functions in the Hasse diagram.
        """
        return [
            self.create_function_from_element(child)
            for child in self.get_hasse_relationships('children')
        ]
