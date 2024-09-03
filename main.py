import sys
from network.network import Network
from network.inconsistency_solution import Inconsistency_Solution
from asp_helper import ASPHelper
from configuration import configuration, update, version, UpdateType
from typing import List

def print_help() -> None:
    print('Model Revision program.')
    print('  Given a model and a set of observations, it determines if the model is consistent. If not, it computes all the minimum number of repair operations in order to render the model consistent.')
    print(f'Version: {version}')
    print('Usage:')
    print('  modrev [-m] model_file [[-obs] observation_files...] [options]')
    print('  options:')
    print('    --model,-m <model_file>\t\tInput model file.')
    print('    --observations,-obs <obs_files...>\tList of observation files.')
    #print('\t\t--output,-o <output_file>\t\tOutput file destination.')
    #print('    --stable-state,-ss <ss_files...>\tList of stable-state observation files')
    print('    --observation-type,-ot <value>\tType of observations in {ts|ss|both}. DEFAULT: ts.')
    print('\t\t\t\t\t\tts   - time-series observations')
    print('\t\t\t\t\t\tss   - stable state observations')
    print('\t\t\t\t\t\tboth - both time-series and stable state observations')
    print('    --update,-up <value>\t\tUpdate mode in {a|s|ma}. DEFAULT: a.')
    print('\t\t\t\t\t\ta  - asynchronous update')
    print('\t\t\t\t\t\ts  - synchronous update')
    print('\t\t\t\t\t\tma - multi-asynchronous update')
    print('    --check-consistency,-cc\t\tCheck the consistency of the model and return without repairing. DEFAULT: false.')
    print('    --exhaustive-search\t\t\tForce exhaustive search of function repair operations. DEFAULT: false.')
    print('    --sub-opt\t\t\t\tShow sub-optimal solutions found. DEFAULT: false.')
    print('    --verbose,-v <value>\t\tVerbose level {0,1,2,3} of output. DEFAULT: 2.')
    print('\t\t\t\t\t\t0  - machine style output (minimalistic easily parsable)')
    print('\t\t\t\t\t\t1  - machine style output (using sets of sets)')
    print('\t\t\t\t\t\t2  - human readable output')
    print('\t\t\t\t\t\t3  - JSON format output')
    print('    --help,-h\t\t\t\tPrint help options.')

def process_arguments(argv: List[str]) -> None:
    if len(argv) < 2:
        print_help()
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
                print_help()
                sys.exit(0)

            if last_opt not in ('--model', '-m', '--observations', '-obs',
                                '--observation-type', '-ot', '--update', 
                                '-up', '--verbose', '-v'):
                print_help()
                raise ValueError('Invalid option ' + last_opt)
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
                print_help()
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
                print_help()
                raise ValueError('Invalid value for option --update: ' + arg)

            if last_opt in ('--verbose', '-v'):
                last_opt = '-m'
                try:
                    value = int(arg)
                    if 0 <= value <= 3:
                        verbose = value
                    else:
                        print_help()
                        raise ValueError('Invalid value for option --verbose: ' + arg)
                except ValueError:
                    print_help()
                    raise ValueError('Invalid value for option --verbose: ' + arg)

    if obs_type in (0, 2):
        network.set_has_ts_obs(True)
    if obs_type in (1, 2):
        network.set_has_ss_obs(True)

def check_consistency(optimization: int) -> List[Inconsistency_Solution]:
    result = []
    # Consistency check
    if configuration['check_asp']:
        # Invoke the consistency check program in ASP
        result = ASPHelper.check_consistency(network, optimization, update.value)
    else:
        # TODO: Add other implementations
        # Convert ASP to SAT or other representation
        # Test consistency
        pass
    return result

def print_consistency(inconsistencies: List[Inconsistency_Solution], optimization: int) -> None:
    print("{")
    print(f'\t"consistent": {"true" if optimization == 0 else "false,"}')
    if optimization != 0:
        print('\t"inconsistencies": [')
        first = True
        for inconsistency in inconsistencies:
            if not first:
                print(",")
            first = False
            print("\t\t{")
            inconsistency.print_inconsistency("\t\t\t")
            print("\t\t}", end="")
        print("\n\t]")
    print("}")

# Model revision procedure
# 1 - tries to repair functions
# 2 - tries to flip the sign of the edges
# 3 - tries to add or remove edges
def model_revision():
    optimization = -2
    f_inconsistencies = check_consistency(optimization)
    if configuration["check_consistency"]:
        print_consistency(f_inconsistencies, optimization)
        return

    if optimization < 0:
        print("ERROR: It is not possible to repair this network for now.")
        print("This may occur if there is at least one node for which from the same input two different outputs are expected (non-deterministic function).")
        return

    # if optimization == 0:
    #     if verbose == 3:
    #         print_consistency(f_inconsistencies, optimization)
    #         return
    #     print("This network is consistent!")
    #     return

    # if Configuration.is_active("debug"):
    #     print(f"found {len(f_inconsistencies)} solutions with {len(f_inconsistencies[0].iNodes_)} inconsistent nodes")

    # # At this point we have an inconsistent network with node candidates to be repaired
    # best_solution = None

    # for inconsistency in f_inconsistencies:
    #     repair_inconsistencies(inconsistency)

    #     # Check for valid solution
    #     if not inconsistency.hasImpossibility:
    #         if best_solution is None or inconsistency.compare_repairs(best_solution) > 0:
    #             best_solution = inconsistency
    #             if Configuration.is_active("debug"):
    #                 print(f"DEBUG: found solution with {best_solution.get_n_topology_changes()} topology changes.")
    #             if best_solution.get_n_topology_changes() == 0 and not Configuration.is_active("allOpt"):
    #                 break
    #     else:
    #         if Configuration.is_active("debug"):
    #             print("DEBUG: Reached an impossibility")

    # if best_solution is None:
    #     print("### It was not possible to repair the model.")
    #     return

    # show_sub_opt = Configuration.is_active("showSolutionForEachInconsistency")

    # if Configuration.is_active("allOpt"):
    #     # TODO: remove duplicates
    #     for inconsistency in f_inconsistencies:
    #         if Configuration.is_active("debug"):
    #             print(f"DEBUG: checking for printing solution with {inconsistency.get_n_topology_changes()} topology changes")
    #         if not inconsistency.hasImpossibility and (inconsistency.compare_repairs(best_solution) >= 0 or show_sub_opt):
    #             if show_sub_opt and inconsistency.compare_repairs(best_solution) < 0:
    #                 if verbose < 2:
    #                     print("+", end="")
    #                 else:
    #                     print("(Sub-Optimal Solution)")
    #             inconsistency.print_solution(verbose)
    # else:
    #     best_solution.print_solution(verbose)

if __name__ == '__main__':
    network = Network() # Creating a new Network instance

    process_arguments(sys.argv)
    parse = ASPHelper.parse_network(network)
    if parse < 1 and not configuration['ignore_warnings']:
        print('#ABORT:\tModel definition with errors.\n\tCheck documentation for input definition details.')
        sys.exit(-1)

    # Main function that revises the model
    model_revision()