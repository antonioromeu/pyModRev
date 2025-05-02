"""
This module contains the SyncUpdater class, which extends the TimeSeriesUpdater
to handle synchronous updates with consistency checks.
"""

import clingo
from updaters.time_series_updater import TimeSeriesUpdater
from updaters.updater import Updater
from network.network import Network
from network.function import Function
from network.inconsistency_solution import Inconsistency_Solution
from configuration import configuration, Inconsistencies


class SyncUpdater(TimeSeriesUpdater):
    """
    This class extends TimeSeriesUpdater and provides specific rules to ensure
    the consistency of updates in a synchronous setting.
    """

    @staticmethod
    def add_specific_rules(ctl: clingo.Control) -> None:
        """
        This method loads a configuration-defined rule set into the control
        object (ctl) and applies consistency constraints based on the provided
        configuration.
        """
        ctl.add('base', [], 'vlabel(P,T+1,V,1) :- 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), not r_part(V), not topologicalerror(V), time(P,T), time(P,T+1).')
        ctl.add('base', [], 'vlabel(P,T+1,V,0) :- {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), not r_gen(V), not topologicalerror(V), time(P,T), time(P,T+1).')
        ctl.add('base', [], 'topologicalerror(V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), vertex(V), {vlabel(P1,T1,V1,S1): vlabel(P2,T2,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V).')
        ctl.add('base', [], 'topologicalerror(V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), exp(P1), exp(P2), P1 != P2, vertex(V), {vlabel(P1,T,V1,S1): vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
        ctl.add('base', [], 'repair(V) :- topologicalerror(V).')
        ctl.add('base', [], '#minimize {1@2,top,V : topologicalerror(V)}.')
        ctl.add('base', [], '#show topologicalerror/1.')
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), not topologicalerror(V), time(P,T), time(P,T+1).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), {noneNegative (P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V), time(P,T), time(P,T+1).')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T1), time(P2,T2), T1!= T2, time(P1,T1+1), time(P2,T2+1), vertex(V), {vlabel( P1,T1,V1,S1): vlabel(P2,T2,V1,S2), S1!=S2, functionAnd(V, Id, V1)}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), exp(P1), exp(P2), P1 < P2, vertex(V), {vlabel(P1,T,V1,S1): vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
            ctl.add('base', [], '#show incT/3.')

    @staticmethod
    def is_func_consistent_with_label_with_profile(
            network: Network,
            labeling: Inconsistency_Solution,
            function: Function,
            profile: str) -> bool:
        """
        Evaluates whether the function's regulatory logic aligns with the expected
        time-dependent behavior of the network, ensuring that the function's
        clauses are satisfied at each time step. It considers both stable states
        and dynamic updates based on the profile's labeling.
        """
        if configuration["debug"]:
            print(f"\n###DEBUG: Checking consistency of function: {function.print_function()} of node {function.get_node_id()}")

        profile_map = labeling.get_v_label()[profile]
        time = 0
        last_val = -1

        while time in profile_map:
            if time + 1 not in profile_map:
                break

            time_map = profile_map[time]
            found_sat = False
            n_clauses = function.get_n_clauses()

            if n_clauses:
                clauses = function.get_clauses()
                for clause in clauses:
                    if Updater.is_clause_satisfiable(clause, network, time_map, function):
                        found_sat = True
                        # In a dynamic update, require a transition to a 1-label at the next time step.
                        if profile_map[time + 1][function.get_node_id()] != 1:
                            return False
                        break

            if not found_sat:
                if n_clauses == 0:
                    if last_val < 0:
                        last_val = time_map[function.get_node_id()]
                    if profile_map[time + 1][function.get_node_id()] != \
                            last_val:
                        return False
                else:
                    if profile_map[time + 1][function.get_node_id()] != 0:
                        return False
            time += 1
        return True

    # @staticmethod
    # def is_func_consistent_with_label(network: Network,
    #                                   labeling: Inconsistency_Solution,
    #                                   function: Function) -> bool:
    #     """
    #     Checks if a function is consistent with a labeling across all profiles.
    #     """
    #     for profile in labeling.get_v_label():
    #         if not SyncUpdater.is_func_consistent_with_label_with_profile(network, labeling, function, profile):
    #             return False
    #     return True

    @staticmethod
    def n_func_inconsistent_with_label_with_profile(
            network: Network,
            labeling: Inconsistency_Solution,
            function: Function,
            profile: str) -> int:
        """
        Checks the consistency of a function with a specific profile in a given
        labeling. It evaluates the function's clauses over time and returns the
        consistency status (consistent, single inconsistency, or double
        inconsistency) based on the profile.
        """
        if configuration["debug"]:
            print(f"\n###DEBUG: Checking consistency of function: {function.print_function()} of node {function.get_node_id()}")

        result = Inconsistencies.CONSISTENT.value
        profile_map = labeling.get_v_label()[profile]
        time = 0
        last_val = -1

        while time in profile_map:
            if (time + 1) not in profile_map:
                break
            time_map = profile_map[time]

            found_sat = False
            n_clauses = function.get_n_clauses()

            if n_clauses:
                clauses = function.get_clauses()
                for clause in clauses:
                    if Updater.is_clause_satisfiable(clause, network, time_map, function):
                        found_sat = True
                        if profile_map[time + 1][function.get_node_id()] != 1:
                            if result in (Inconsistencies.CONSISTENT.value,
                                          Inconsistencies.SINGLE_INC_PART.value):
                                result = Inconsistencies.SINGLE_INC_PART.value
                            else:
                                return Inconsistencies.DOUBLE_INC.value
                        break
            if not found_sat:
                if n_clauses == 0:
                    if last_val < 0:
                        last_val = time_map[function.get_node_id()]
                    if profile_map[time + 1][function.get_node_id()] != \
                            last_val:
                        return Inconsistencies.DOUBLE_INC.value
                else:
                    if profile_map[time + 1][function.get_node_id()] != 0:
                        if result in (Inconsistencies.CONSISTENT.value,
                                      Inconsistencies.SINGLE_INC_GEN.value):
                            result = Inconsistencies.SINGLE_INC_GEN.value
                        else:
                            return Inconsistencies.DOUBLE_INC.value
            time += 1
        return result

    # @staticmethod
    # def n_func_inconsistent_with_label(
    #         network: Network,
    #         labeling: Inconsistency_Solution,
    #         function: Function) -> int:
    #     """
    #     Checks the consistency of a function against a labeling. It verifies each
    #     profile and returns the consistency status (consistent, inconsistent, or
    #     double inconsistency).
    #     """
    #     result = Inconsistencies.CONSISTENT.value

    #     # Verify for each profile
    #     for key, _ in labeling.get_v_label().items():
    #         ret = SyncUpdater.n_func_inconsistent_with_label_with_profile(network, labeling,
    #                                                         function, key)
    #         if configuration["debug"]:
    #             print(f"DEBUG: Consistency value: {ret} for node {function.get_node_id()} with function: {function.print_function()}")

    #         if result == Inconsistencies.CONSISTENT.value:
    #             result = ret
    #         else:
    #             if ret not in (result, Inconsistencies.CONSISTENT.value):
    #                 result = Inconsistencies.DOUBLE_INC.value
    #                 break
    #     return result
