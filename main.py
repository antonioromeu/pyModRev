import sys
from network.network import Network
from asp_helper import ASPHelper
from enum import Enum
from typing import List

def process_arguments(argv: List[str]):
    if len(argv) < 2:
        # print_help()
        raise ValueError('Invalid number of arguments')

    # Observation type
    # 0 - time-series observations [default]
    # 1 - stable state observations
    # 2 - both (time-series + stable state)
    obs_type = 0
    last_opt = '-m'

    for arg in argv:
        if arg == 'main.py':
            continue
        if arg.startswith('-'):
            if arg == '--sub-opt':
                configuration['show_solution_for_each_inconsistency'] = True
                continue
            if arg == '--exhaustive-search':
                configuration['force_optimum'] = True
                continue
            if arg == '--check-consistency' or arg == '-cc':
                configuration['check_consistency'] = True
                continue

            # Retro-compatibility option
            if arg == '--steady-state' or arg == '--ss':
                obs_type = 1
                continue

            last_opt = arg
            if last_opt in ('--help', '-h'):
                # print_help()
                sys.exit(0)

            if last_opt not in ('--model', '-m', '--observations', '-obs',
                                '--observation-type', '-ot', '--update', 
                                '-up', '--verbose', '-v'):
                # print_help()
                raise ValueError('Invalid option' + last_opt)
        else:
            if last_opt in ('--model', '-m'):
                if not network.get_input_file_network():
                    network.set_input_file_network(arg)
                else:
                    network.add_observation_file(arg)
                continue
            if last_opt in ('--observations', '-obs'):
                network.add_observation_file(arg)
                continue
            if last_opt in ('--observation-type', '-ot'):
                last_opt = '-m'
                if arg == 'ts':
                    obs_type = 0
                    continue
                if arg == 'ss':
                    obs_type = 1
                    continue
                if arg == 'both':
                    obs_type = 2
                    continue
                # print_help()
                raise ValueError('Invalid value for option --observation-type: ' + arg)

            if last_opt in ('--update', '-up'):
                last_opt = '-m'
                if arg == 'a':
                    update = UpdateType.ASYNC
                    continue
                if arg == 's':
                    update = UpdateType.SYNC
                    continue
                if arg == 'ma':
                    update = UpdateType.MASYNC
                    continue
                # print_help()
                raise ValueError('Invalid value for option --update: ' + arg)

            if last_opt in ('--verbose', '-v'):
                last_opt = '-m'
                try:
                    value = int(arg)
                    if 0 <= value <= 3:
                        verbose = value
                    else:
                        # print_help()
                        raise ValueError('Invalid value for option --verbose: ' + arg)
                except ValueError:
                    # print_help()
                    raise ValueError('Invalid value for option --verbose: ' + arg)

    if obs_type in (0, 2):
        network.set_has_ts_obs(True)
    if obs_type in (1, 2):
        network.set_has_ss_obs(True)

if __name__ == '__main__':
    class Inconsistencies(Enum):
        CONSISTENT = 0
        SINGLE_INC_GEN = 1
        SINGLE_INC_PART = 2
        DOUBLE_INC = 3

    class UpdateType(Enum):
        ASYNC = 0
        SYNC = 1
        MASYNC = 2

    # Verbose level
    # 0 - machine style output (minimalistic easily parsable)
    # 1 - machine style output (using set of sets)
    # 2 - human readable output [default]
    verbose = 2
    version = '1.0.0'
    configuration = {}
    update = UpdateType.ASYNC # Setting the update type to ASYNC
    network = Network() # Creating a new Network instance

    process_arguments(sys.argv)
    parse = ASPHelper.parse_network(network)