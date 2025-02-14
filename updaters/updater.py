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
from configuration import UpdateType
from network.network import Network


class Updater(ABC):
    """
    The Updater class is the base class for all update-related logic. It \
        defines
    the structure for applying update rules, checking consistency, and \
        selecting
    the correct updater based on the update type. This class should be extended
    to implement specific update types such as synchronous, asynchronous, or
    multi-asynchronous updates.
    """

    @staticmethod
    @abstractmethod
    def apply_update_rules(ctl: clingo.Control, update_type: int,
                           configuration) -> None:
        """
        Subclasses must implement this method to apply update rules based on
        the update type (e.g., synchronous, asynchronous, etc.).
        """

    @staticmethod
    def get_updater(update_type: int) -> "Updater":
        """
        This method returns the appropriate subclass of Updater based on the
        provided update type.
        """
        if update_type == UpdateType.ASYNC.value:
            from updaters.async_updater import AsyncUpdater
            return AsyncUpdater
        if update_type == UpdateType.SYNC.value:
            from updaters.sync_updater import SyncUpdater
            return SyncUpdater
        if update_type == UpdateType.MASYNC.value:
            from updaters.complete_updater import CompleteUpdater
            return CompleteUpdater
        raise ValueError(f"Invalid update type: {update_type}")

    @staticmethod
    def check_consistency(network: Network, update_type: int, configuration) \
            -> Tuple[List, int]:
        """
        This method loads the necessary rules, including base rules and network
        observation files, and applies consistency checks to the network. It \
            also
        handles the logic for checking the optimization based on the update \
            type.
        """
        result = []
        optimization = -2
        try:
            def logger(warning_code, message):
                if configuration['debug']:
                    print(warning_code, file=sys.stderr)
                    print(message, file=sys.stderr)

            ctl = clingo.Control(['--opt-mode=optN'], logger, 20)
            # ctl.load(configuration['asp_cc_base'])
            ctl.add('base', [], 'sign(0;1).')
            ctl.add('base', [], 'complement(T,S) :- sign(S),sign(T),T!=S.')
            ctl.add('base', [], 'vertex(V) :- edge(V,_,_).')
            ctl.add('base', [], 'vertex(V) :- edge(_,V,_).')
            ctl.add('base', [], '{r_gen(V)} :- vertex(V), not fixed(V).')
            ctl.add('base', [], '{r_part(V)} :- vertex(V), not fixed(V).')
            ctl.add('base', [], 'repair(V) :- r_gen(V).')
            ctl.add('base', [], 'repair(V) :- r_part(V).')
            ctl.add('base', [], '#show repair/1.')
            ctl.add('base', [], '#show r_gen/1.')
            ctl.add('base', [], '#show r_part/1.')

            has_ss_obs = network.get_has_ss_obs()
            has_ts_obs = network.get_has_ts_obs()

            if has_ss_obs:
                from updaters.steady_state_updater import SteadyStateUpdater
                SteadyStateUpdater.apply_update_rules(ctl, update_type,
                                                      configuration)

            if has_ts_obs:
                from updaters.time_series_updater import TimeSeriesUpdater
                TimeSeriesUpdater.apply_update_rules(ctl, update_type,
                                                     configuration)

            ctl.load(network.get_input_file_network())
            for obs_file in network.get_observation_files():
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
        return result, optimization
