"""
This module contains the Updater class, which serves as an abstract base class
for applying update rules based on different update types. It provides utility
methods for consistency checks and loading appropriate update logic based on
the configuration.
"""

import sys
from abc import ABC, abstractmethod
from typing import List, Tuple
import clingo
from network.network import Network
from network.function import Function
from network.inconsistency_solution import Inconsistency_Solution
from configuration import configuration


class Updater(ABC):
    """
    The Updater class is the base class for all update-related logic. It
    defines the structure for applying update rules, checking consistency, and
    selecting the correct updater based on the update type. This class should
    be extended to implement specific update types such as synchronous,
    asynchronous, or complete updates.
    """

    @staticmethod
    @abstractmethod
    def apply_update_rules(ctl: clingo.Control, updater) -> None:
        """
        Subclasses must implement this method to apply update rules based on
        the update type (e.g., synchronous, asynchronous, etc.).
        """

    @staticmethod
    @abstractmethod
    def is_func_consistent_with_label_with_profile(
            network: Network,
            labeling: Inconsistency_Solution,
            function: Function,
            profile: str) -> bool:
        """
        Evaluates whether the function's regulatory logic aligns with the
        expected dynamic behavior of the network. This implementation assumes a
        time series (i.e. multiple time points) and does not handle a
        steady-state scenario.
        """

    @staticmethod
    @abstractmethod
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

    @staticmethod
    def check_consistency(network: Network) -> Tuple[List, int]:
        """
        This method loads the necessary rules, including base rules and network
        observation files, and applies consistency checks to the network. It
        also handles the logic for checking the optimization based on the
        update type.
        """
        result = []
        optimization = -2
        try:
            def logger(warning_code, message):
                if configuration['debug']:
                    print(warning_code, file=sys.stderr)
                    print(message, file=sys.stderr)
            # TODO confirmar se é necessário um clingo novo para cada obs/updater
            for obs_file, updater in network.get_observation_files_with_updater():
                ctl = clingo.Control(['--opt-mode=optN'], logger, 20)
                ctl.add('base', [], 'sign(0;1).')
                ctl.add('base', [], 'complement(T,S) :- sign(S),sign(T),T!=S.')
                ctl.add('base', [], 'vertex(V) :- edge(V,_,_).')
                ctl.add('base', [], 'vertex(V) :- edge(_,V,_).')
                ctl.add('base', [], '{r_gen(V)} :- vertex(V), not fixed(V).')
                ctl.add('base', [], '{r_part(V)} :- vertex(V), not fixed(V).')
                ctl.add('base', [], 'repair(V) :- r_gen(V).')
                ctl.add('base', [], 'repair(V) :- r_part(V).')
                # TODO confirmar se estas linhas são necessárias
                ctl.add('base', [], '#show repair/1.')
                ctl.add('base', [], '#show r_gen/1.')
                ctl.add('base', [], '#show r_part/1.')
                ctl.load(network.get_input_file_network())
                non_steady_updaters = set()
                from updaters.async_updater import AsyncUpdater
                from updaters.sync_updater import SyncUpdater
                from updaters.steady_state_updater import SteadyStateUpdater
                from updaters.complete_updater import CompleteUpdater
                if type(updater).__name__ != SteadyStateUpdater.__name__:
                    if type(updater).__name__ == SyncUpdater.__name__:
                        non_steady_updaters.add('SyncUpdater')
                    elif type(updater).__name__ == AsyncUpdater.__name__:
                        non_steady_updaters.add('AsyncUpdater')
                    elif type(updater).__name__ == CompleteUpdater.__name__:
                        non_steady_updaters.add('CompleteUpdater')
                    else:
                        raise Exception("Unknown non-steady state updater type encountered")
                    if len(non_steady_updaters) > 1:
                        raise Exception(f"Conflicting updater types detected: {', '.join(non_steady_updaters)} cannot coexist.")
                updater.apply_update_rules(ctl, updater)
                ctl.load(obs_file)
                ctl.ground([('base', [])])
                with ctl.solve(yield_=True) as handle:
                    if handle.get().satisfiable:
                        for model in handle:
                            if model and model.optimality_proven:
                                from asp_helper import ASPHelper
                                res, opt = ASPHelper.parse_cc_model(model)
                                result.append(res)
                                optimization = opt
                    else:
                        optimization = -1
        except Exception as e:
            print(f'Failed to check consistency: {e}')
            sys.exit(-1)
        return result, optimization

    @staticmethod
    def is_clause_satisfiable(clause, network, time_map, function) -> bool:
        """
        Evaluates whether a clause is satisfiable given the network and current time mapping.
        """
        regulators = function.bitarray_to_regulators(clause)
        for var in regulators:
            edge = network.get_edge(var, function.get_node_id())
            if edge is not None:
                # The clause is unsatisfied if the edge sign contradicts the value in time_map.
                if (edge.get_sign() > 0) == (time_map[var] == 0):
                    return False
            else:
                print(f"WARN: Missing edge from {var} to {function.get_node_id()}")
                return False
        return True

    # @staticmethod
    # def get_updater(update_type: int) -> "Updater":
    #     """
    #     This method returns the appropriate subclass of Updater based on the
    #     provided update type.
    #     """
    #     if update_type == UpdateType.ASYNC.value:
    #         from updaters.async_updater import AsyncUpdater
    #         return AsyncUpdater
    #     if update_type == UpdateType.SYNC.value:
    #         from updaters.sync_updater import SyncUpdater
    #         return SyncUpdater
    #     if update_type == UpdateType.MASYNC.value:
    #         from updaters.complete_updater import CompleteUpdater
    #         return CompleteUpdater
    #     raise ValueError(f"Invalid update type: {update_type}")

    # @staticmethod
    # def check_consistency(network: Network, update_type: int) -> Tuple[List, int]:
    #     """
    #     This method loads the necessary rules, including base rules and network
    #     observation files, and applies consistency checks to the network. It
    #     also handles the logic for checking the optimization based on the
    #     update type.
    #     """
    #     result = []
    #     optimization = -2
    #     try:
    #         def logger(warning_code, message):
    #             if configuration['debug']:
    #                 print(warning_code, file=sys.stderr)
    #                 print(message, file=sys.stderr)

    #         ctl = clingo.Control(['--opt-mode=optN'], logger, 20)
    #         # ctl.load(configuration['asp_cc_base'])
    #         ctl.add('base', [], 'sign(0;1).')
    #         ctl.add('base', [], 'complement(T,S) :- sign(S),sign(T),T!=S.')
    #         ctl.add('base', [], 'vertex(V) :- edge(V,_,_).')
    #         ctl.add('base', [], 'vertex(V) :- edge(_,V,_).')
    #         ctl.add('base', [], '{r_gen(V)} :- vertex(V), not fixed(V).')
    #         ctl.add('base', [], '{r_part(V)} :- vertex(V), not fixed(V).')
    #         ctl.add('base', [], 'repair(V) :- r_gen(V).')
    #         ctl.add('base', [], 'repair(V) :- r_part(V).')
    #         ctl.add('base', [], '#show repair/1.')
    #         ctl.add('base', [], '#show r_gen/1.')
    #         ctl.add('base', [], '#show r_part/1.')

    #         has_ss_obs = network.get_has_ss_obs()
    #         has_ts_obs = network.get_has_ts_obs()

    #         if has_ss_obs:
    #             from updaters.steady_state_updater import SteadyStateUpdater
    #             SteadyStateUpdater.apply_update_rules(ctl, update_type)

    #         if has_ts_obs:
    #             from updaters.time_series_updater import TimeSeriesUpdater
    #             TimeSeriesUpdater.apply_update_rules(ctl, update_type)

    #         ctl.load(network.get_input_file_network())
    #         for obs_file in network.get_observation_files():
    #             ctl.load(obs_file)
    #             print(updater)
    #             ctl.ground([('base', [])])
    #             with ctl.solve(yield_=True) as handle:
    #                 if handle.get().satisfiable:
    #                     for model in handle:
    #                         if model and model.optimality_proven:
    #                             from asp_helper import ASPHelper
    #                             res, opt = ASPHelper.parse_cc_model(model)
    #                             result.append(res)
    #                             optimization = opt
    #                 else:
    #                     optimization = -1
    #     except Exception as e:
    #         print(f'Failed to check consistency: {e}')
    #     return result, optimization

    # @staticmethod
    # @abstractmethod
    # def is_func_consistent_with_label(
    #         network: Network,
    #         labeling: Inconsistency_Solution,
    #         function: Function) -> int:
    #     """
    #     Checks if a function is consistent with a labeling across all profiles.
    #     """

    # @staticmethod
    # @abstractmethod
    # def n_func_inconsistent_with_label(
    #         network: Network,
    #         labeling: Inconsistency_Solution,
    #         function: Function) -> int:
    #     """
    #     Checks the consistency of a function against a labeling. It verifies
    #     each profile and returns the consistency status (consistent,
    #     inconsistent, or double inconsistency).
    #     """
