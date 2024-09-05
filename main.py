import sys
from network.network import Network
from network.edge import Edge
from network.function import Function
from network.inconsistency_solution import Inconsistency_Solution
from network.inconsistent_node import Inconsistent_Node
from asp_helper import ASPHelper
from configuration import configuration, update, version, verbose, UpdateType
from typing import List, Tuple

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

def check_consistency() -> Tuple[List[Inconsistency_Solution], int]:
    result = []
    optimization = -2
    # Consistency check
    if configuration['check_asp']:
        # Invoke the consistency check program in ASP
        result, optimization = ASPHelper.check_consistency(network, update.value)
    else:
        # TODO: Add other implementations
        # Convert ASP to SAT or other representation
        # Test consistency
        pass
    return result, optimization

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

# This function receives an inconsistent model with a set of nodes to be repaired and 
# tries  to repair the target nodes making the model consistent
# returning the set of repair operations to be applied
def repair_inconsistencies(inconsistency: Inconsistency_Solution) -> None:
    # Repair each inconsistent node
    for node_id, node in inconsistency.get_i_nodes().items():
        repair_node_consistency(inconsistency, node)
        
        if inconsistency.get_has_impossibility():
            # One of the nodes was impossible to repair
            if configuration["debug"]:
                print(f"#Found a node with impossibility - {node_id}")
            return

        if configuration["debug"]:
            print(f"#Found a repair for node - {node_id}")

# This function repairs a given node and determines all possible solutions
# consider 0 .. N add/remove repair operations, starting with 0 repairs of this type
def repair_node_consistency(inconsistency: Inconsistency_Solution, inconsistent_node: Inconsistent_Node) -> None:
    original_node = network.get_node(inconsistent_node.get_id())
    original_function = original_node.get_function()
    original_regulators = original_function.get_regulators() if original_function is not None else []
    original_regulators_by_term = original_function.get_regulators_by_term() if original_function is not None else {}
    list_edges_remove = []
    list_edges_add = []

    for regulator in original_regulators: # TODO confirm if it is the correct translation
        edge = network.get_edge(regulator, original_function.get_node_id())
        if edge is not None and not edge.get_fixed():
            list_edges_remove.append(edge)

    max_n_remove = len(list_edges_remove)
    max_n_add = len(network.get_nodes()) - max_n_remove

    for node_id, node in network.get_nodes().items():
        is_original_regulator = any(node_id == reg_id for reg_id in original_regulators)

        if not is_original_regulator:
            new_edge = Edge(node, original_node, 1) # TODO understand why self pointing edge is being added?
            list_edges_add.append(new_edge)

    sol_found = False

    # Iterate through the number of add/remove operations
    for n_operations in range(max_n_remove + max_n_add + 1):
        for n_add in range(n_operations + 1):
            if n_add > max_n_add:
                break
            n_remove = n_operations - n_add
            if n_remove > max_n_remove:
                continue
            if configuration["debug"]:
                print(f"DEBUG: Testing {n_add} adds and {n_remove} removes")

            list_add_combination = get_edges_combinations(list_edges_add, n_add)
            list_remove_combination = get_edges_combinations(list_edges_remove, n_remove)

            for add_combination in list_add_combination:
                for remove_combination in list_remove_combination:
                    is_sol = False

                    # Remove and add edges
                    for edge in remove_combination:
                        if configuration["debug"]:
                            print(f"DEBUG: remove edge from {edge.get_start_node().get_id()}")
                        network.remove_edge(edge.get_start_node(), edge.get_end_node())

                    for edge in add_combination:
                        if configuration["debug"]:
                            print(f"DEBUG: add edge from {edge.get_start_node().get_id()}")
                        network.add_edge(edge.get_start_node(), edge.get_end_node(), edge.get_sign())

                    # If n_operations > 0, the function must be changed
                    if n_operations > 0:
                        new_function = Function(original_node.get_id())
                        clause_id = 1

                        for regulator in original_regulators:
                            removed = any(regulator == edge.get_start_node().get_id() for edge in remove_combination)
                            if not removed:
                                new_function.add_regulator_to_term(clause_id, regulator) # TODO try using add_regulator_to_term and only when needed add the clause
                                clause_id += 1

                        for edge in add_combination:
                            new_function.add_regulator_to_term(clause_id, edge.get_start_node().get_id())
                            clause_id += 1

                        original_node.add_function(new_function)
                    
                    # Test with edge flips starting with 0 edge flips
                    is_sol = repair_node_consistency_flipping_edges(inconsistency, inconsistent_node, add_combination, remove_combination)

                    # Add and remove edges for the original network
                    for edge in remove_combination:
                        network.add_edge(edge.get_start_node(), edge.get_end_node(), edge.get_sign())

                    for edge in add_combination:
                        network.remove_edge(edge.get_start_node(), edge.get_end_node())

                    # Restore the original function
                    original_node.add_function(original_function)

                    if is_sol:
                        sol_found = True
                        if not configuration["allOpt"]:
                            if configuration["debug"]:
                                print("DEBUG: no more solutions - allOpt")
                            return

            # Clean up memory
            list_add_combination.clear()
            list_remove_combination.clear()

        if sol_found:
            break

    if not sol_found:
        inconsistency.has_impossibility = True
        print(f"WARN: Not possible to repair node {inconsistent_node.get_id()}")

    # Clean up memory
    list_edges_remove.clear()
    list_edges_add.clear()

def repair_node_consistency_flipping_edges(inconsistency: Inconsistency_Solution, inconsistent_node: Inconsistent_Node, added_edges: List[Edge], removed_edges: List[Edge]):
    f = network.get_node(inconsistent_node.get_id()).get_function()

    edge_map = f.get_regulators_map() if f is not None else {}
    list_edges = []

    for regulator_id in edge_map.keys():
        e = network.get_edge(regulator_id, f.get_node())
        if e is not None and not e.is_fixed():
            list_edges.append(e)

    if configuration["debug"]:
        print(f"DEBUG: searching solution flipping edges for {inconsistent_node.get_id()}")

    sol_found = False
    iterations = len(list_edges)

    # Limit the number of flip edges if the node has already been repaired
    if inconsistent_node.is_repaired():
        iterations = inconsistent_node.get_n_flip_edges_operations()

    for n_edges in range(iterations + 1):
        if configuration["debug"]:
            print(f"DEBUG: testing with {n_edges} edge flips")

        e_candidates = get_edges_combinations(list_edges, n_edges)

        # For each set of flipping edges
        for edge_set in e_candidates:
            # Flip all edges
            for edge in edge_set:
                edge.flip_sign()
                if configuration["debug"]:
                    print(f"DEBUG: flip edge from {edge.start_.id_}")

            is_sol = repair_node_consistency_functions(inconsistency, inconsistent_node, edge_set, added_edges, removed_edges)

            # Put network back to normal by flipping edges back
            for edge in edge_set:
                edge.flip_sign()
                if configuration["debug"]:
                    print(f"DEBUG: return flip edge from {edge.start_.id_}")

            if is_sol:
                if configuration["debug"]:
                    print("DEBUG: is solution by flipping edges")
                sol_found = True
                if not configuration["all_opt"]:
                    if configuration["debug"]:
                        print("DEBUG: no more solutions - allOpt")
                    return True

        if sol_found:
            if configuration["debug"]:
                print(f"DEBUG: ready to end with {n_edges} edges flipped")
            break

    return sol_found

def get_edges_combinations(edges: List[Edge], n: int, index_start: int = 0) -> List[List[Edge]]:
    if n == 0:
        return [[]]
    result = []
    for i in range(index_start, len(edges) - n + 1):
        if n > 1:
            aux = get_edges_combinations(edges, n - 1, i + 1)
            for combination in aux:
                combination.append(edges[i])
                result.append(combination)
        else:
            result.append([edges[i]])
    return result

# Model revision procedure
# 1 - tries to repair functions
# 2 - tries to flip the sign of the edges
# 3 - tries to add or remove edges
def model_revision():
    optimization = -2
    f_inconsistencies, optimization = check_consistency()
    if configuration["check_consistency"]:
        print_consistency(f_inconsistencies, optimization)
        return

    if optimization < 0:
        print("ERROR: It is not possible to repair this network for now.")
        print("This may occur if there is at least one node for which from the same input two different outputs are expected (non-deterministic function).")
        return

    if optimization == 0:
        if verbose == 3:
            print_consistency(f_inconsistencies, optimization)
            return
        print("This network is consistent!")
        return

    if configuration["debug"]:
        print(f"Found {len(f_inconsistencies)} solution(s) with {len(f_inconsistencies[0].get_i_nodes())} inconsistent node(s)")

    # At this point we have an inconsistent network with node candidates to be repaired
    best_solution = None

    for inconsistency in f_inconsistencies:
        repair_inconsistencies(inconsistency)

        # Check for valid solution
        # if not inconsistency.hasImpossibility:
        #     if best_solution is None or inconsistency.compare_repairs(best_solution) > 0:
        #         best_solution = inconsistency
        #         if Configuration.is_active("debug"):
        #             print(f"DEBUG: found solution with {best_solution.get_n_topology_changes()} topology changes.")
        #         if best_solution.get_n_topology_changes() == 0 and not Configuration.is_active("allOpt"):
        #             break
        # else:
        #     if Configuration.is_active("debug"):
        #         print("DEBUG: Reached an impossibility")

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