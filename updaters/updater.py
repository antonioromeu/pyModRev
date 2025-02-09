import sys
import clingo
from abc import ABC, abstractmethod
from typing import List, Tuple
from configuration import UpdateType
from network.network import Network

class Updater(ABC):
    @abstractmethod
    def apply_update_rules(ctl, configuration):
        pass

    @staticmethod
    def get_updater(update_type: int) -> "Updater":
        from updaters.sync_updater import SyncUpdater
        from updaters.async_updater import AsyncUpdater
        from updaters.multi_async_updater import MultiAsyncUpdater
        updaters = {
            UpdateType.SYNC.value: SyncUpdater,
            UpdateType.ASYNC.value: AsyncUpdater,
            UpdateType.MASYNC.value: MultiAsyncUpdater
        }
        if update_type not in updaters:
            raise ValueError(f"Invalid update type: {update_type}")
        print(updaters[update_type])
        return updaters[update_type]

    @staticmethod
    def check_consistency(network: Network, update_type, configuration) -> Tuple[List, int]:
        result = []
        optimization = -2
        try:
            def logger(warning_code, message):
                if configuration['debug']:
                    print(warning_code, file=sys.stderr)
                    print(message, file=sys.stderr)
            ctl = clingo.Control(['--opt-mode=optN'], logger, 20)
            ctl.load(configuration['asp_cc_base'])
            if network.get_has_ss_obs():
                from updaters.steady_state_updater import SteadyStateUpdater
                SteadyStateUpdater.apply_update_rules(ctl, configuration)
            if network.get_has_ts_obs():
                from updaters.time_series_updater import TimeSeriesUpdater
                TimeSeriesUpdater.apply_update_rules(ctl, update_type, configuration)
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