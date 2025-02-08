import sys
import clingo
from abc import ABC, abstractmethod
from typing import List, Tuple
from asp_helper import ASPHelper

class Updater(ABC):
    def __init__(self, update_type):
        self.update_type = update_type

    @abstractmethod
    def apply_update_rules(self, ctl):
        pass

    def check_consistency(self, network, configuration) -> Tuple[List, int]:
        result = []
        optimization = -2
        try:
            def logger(warning_code, message):
                if configuration['debug']:
                    print(warning_code, file=sys.stderr)
                    print(message, file=sys.stderr)
            ctl = clingo.Control(['--opt-mode=optN'], logger, 20)
            ctl.load(configuration['asp_cc_base'])
            self.apply_update_rules(ctl, network, configuration)
            ctl.load(network.get_input_file_network())
            for obs_file in network.get_observation_files():
                ctl.load(obs_file)
            ctl.ground([('base', [])])
            with ctl.solve(yield_=True) as handle:
                if handle.get().satisfiable:
                    for model in handle:
                        if model and model.optimality_proven:
                            res, opt = ASPHelper.parse_cc_model(model)
                            result.append(res)
                            optimization = opt
                else:
                    optimization = -1
        except Exception as e:
            print(f'Failed to check consistency: {e}')
        return result, optimization