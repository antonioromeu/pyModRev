"""
This module contains the SteadyStateUpdater class, which extends the Updater
class to handle steady-state updates while ensuring consistency constraints.
"""

import clingo
from updaters.updater import Updater
from network.network import Network
from network.function import Function
from network.inconsistency_solution import Inconsistency_Solution
from configuration import configuration


class SteadyStateUpdater(Updater):
    """
    This class extends Updater and applies specific rules to ensure
    consistent updates in a steady-state system.
    """

    @staticmethod
    def apply_update_rules(ctl: clingo.Control, update_type: int) -> None:
        """
        This method loads configuration-defined rules into the control object
        (ctl) and applies consistency constraints based on the provided
        configuration.
        """
        # ctl.load(configuration['asp_cc_ss'])
        ctl.add('base', [], 'ss(P) :- exp(P), not time(P,_).')
        ctl.add('base', [], '1{vlabel(P,V,S):sign(S)}1 :- vertex(V), ss(P).')
        ctl.add('base', [], ':-vlabel(P,V,S1), obs_vlabel(P,V,S2),complement(S1,S2).')
        ctl.add('base', [], 'onePositive(P,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S), vlabel(P,V2,S), ss(P).')
        ctl.add('base', [], 'oneNegative(P,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S), vlabel(P,V2,T), complement(S,T), ss(P).')
        ctl.add('base', [], 'noneNegative(P,V,Id) :- onePositive(P,V,Id), not oneNegative(P,V,Id).')
        ctl.add('base', [], 'vlabel(P,V,1) :- 1{noneNegative(P,V,Id):functionOr(V,Id)}, vertex(V), ss(P), not r_part(V).')
        ctl.add('base', [], 'vlabel(P,V,0) :- {noneNegative(P,V,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_), not r_gen(V).')
        ctl.add('base', [], '#minimize {1,V : repair(V)}.')
        ctl.add('base', [], '#minimize {1,g,V : r_gen(V)}.')
        ctl.add('base', [], '#minimize {1,p,V : r_part(V)}.')
        ctl.add('base', [], '#show vlabel/3.')
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,0), 1{noneNegative(P,V\
                    ,Id):functionOr(V,Id)}, vertex(V), ss(P), r_part(V).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,1), {noneNegative(P,V \
                    ,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_)\
                    , r_gen(V).')
            ctl.add('base', [], '#show inc/2.')

    @staticmethod
    def is_func_consistent_with_label_with_profile(network, labeling, function, profile) -> bool:
        """
        Evaluates whether the function's regulatory logic aligns with the
        expected steady-state behavior of the network. This method assumes a
        single time mapping is present in the label profile.
        """
        if configuration["debug"]:
            print(f"\n###DEBUG: Checking steady-state consistency of function: {function.print_function()} of node {function.get_node_id()}")

        profile_map = labeling.get_v_label()[profile]
        # For steady state, we expect exactly one time mapping
        if len(profile_map) != 1:
            print("ERROR: SteadyStateUpdater expects a single time mapping.")
            return False

        # Retrieve the unique time mapping
        time_key = next(iter(profile_map))
        time_map = profile_map[time_key]
        found_sat = False
        n_clauses = function.get_n_clauses()

        if n_clauses:
            # Evaluate each clause until one is satisfiable.
            for clause in function.get_clauses():
                if SteadyStateUpdater.is_clause_satisfiable(clause, network, time_map, function):
                    # In steady state, a satisfied clause means the function’s output should be 1.
                    found_sat = True
                    return time_map[function.get_node_id()] == 1
        if not found_sat:
            return n_clauses == 0 or time_map[function.get_node_id()] == 0
        return True

    @staticmethod
    def is_func_consistent_with_label(network: Network,
                                      labeling: Inconsistency_Solution,
                                      function: Function) -> int:
        """
        Checks if a function is consistent with a labeling across all profiles.
        """
        for profile in labeling.get_v_label():
            # if not Updater.is_func_consistent_with_label_with_profile(network, labeling, function, profile):
            if not SteadyStateUpdater.is_func_consistent_with_label_with_profile(network, labeling, function, profile):
                return False
        return True

    @staticmethod
    def is_clause_satisfiable(clause, network, time_map, function) -> bool:
        """
        Evaluates whether a clause is satisfiable given the network and the steady-state time mapping.
        """
        regulators = function.bitarray_to_regulators(clause)
        for var in regulators:
            edge = network.get_edge(var, function.get_node_id())
            if edge is not None:
                # In the steady state, if the sign of the edge contradicts the current value,
                # the clause is unsatisfied.
                if (edge.get_sign() > 0) == (time_map[var] == 0):
                    return False
            else:
                print(f"WARN: Missing edge from {var} to {function.get_node_id()}")
                return False
        return True
