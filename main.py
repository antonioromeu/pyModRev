import sys
import math
from network.network import Network
from network.edge import Edge
from network.function import Function
from network.inconsistency_solution import Inconsistency_Solution
from network.inconsistent_node import Inconsistent_Node
from network.repair_set import Repair_Set
from asp_helper import ASPHelper
from configuration import configuration, update, version, verbose, UpdateType, Inconsistencies
from typing import List, Tuple
from bitarray import bitarray

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
                            new_function.add_regulator_to_term(clause_id, edge.get_start_node().get_id()) # TODO try using add_regulator_to_term and only when needed add the clause
                            clause_id += 1

                        # TODO does this makes sense? only creating the PFH function if the new function has regulators?
                        if len(new_function.get_regulators()):
                            new_function.create_pfh_function()
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
                        if not configuration["all_opt"]:
                            if configuration["debug"]:
                                print("DEBUG: no more solutions - all_opt")
                            return
        if sol_found:
            break
    if not sol_found:
        inconsistency.set_impossibility(True)
        print(f"WARN: Not possible to repair node {inconsistent_node.get_id()}")

def repair_node_consistency_flipping_edges(inconsistency: Inconsistency_Solution, inconsistent_node: Inconsistent_Node, added_edges: List[Edge], removed_edges: List[Edge]) -> bool:
    function = network.get_node(inconsistent_node.get_id()).get_function()

    regulators = function.get_regulators() if function is not None else {}
    list_edges = []

    for regulator in regulators:
        edge = network.get_edge(regulator, function.get_node_id())
        if edge is not None and not edge.get_fixed():
            list_edges.append(edge)

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

        edges_candidates = get_edges_combinations(list_edges, n_edges)

        # For each set of flipping edges
        for edge_set in edges_candidates:
            # Flip all edges
            for edge in edge_set:
                edge.flip_sign()
                if configuration["debug"]:
                    print(f"DEBUG: flip edge from {edge.get_start_node().get_id()}")

            is_sol = repair_node_consistency_functions(inconsistency, inconsistent_node, edge_set, added_edges, removed_edges)

            # Put network back to normal by flipping edges back
            for edge in edge_set:
                edge.flip_sign()
                if configuration["debug"]:
                    print(f"DEBUG: return flip edge from {edge.get_start_node().get_id()}")

            if is_sol:
                if configuration["debug"]:
                    print("DEBUG: is solution by flipping edges")
                sol_found = True
                if not configuration["all_opt"]:
                    if configuration["debug"]:
                        print("DEBUG: no more solutions - all_opt")
                    return True

        if sol_found:
            if configuration["debug"]:
                print(f"DEBUG: ready to end with {n_edges} edges flipped")
            break

    return sol_found

# Repairs the function of the node, if necessary
def repair_node_consistency_functions(inconsistency: Inconsistency_Solution, inconsistent_node: Inconsistent_Node, flipped_edges: List[Edge], added_edges: List[Edge], removed_edges: List[Edge]) -> bool:
    sol_found = False
    repair_type = inconsistent_node.get_repair_type()
    
    # If any topological operation was performed, validate if the model became consistent
    if flipped_edges or added_edges or removed_edges:
        repair_type = n_func_inconsistent_with_label(inconsistency, network.get_node(inconsistent_node.get_id()).get_function())
        if repair_type == Inconsistencies.CONSISTENT:
            if configuration["debug"]:
                print("DEBUG: node consistent with only topological changes")
            
            repair_set = Repair_Set()

            for edge in flipped_edges:
                repair_set.add_flipped_edge(edge)

            # Add and remove edges in the solution repair set
            for edge in removed_edges:
                repair_set.remove_edge(edge)

            for edge in added_edges:
                repair_set.add_edge(edge)

            if added_edges or removed_edges:
                repair_set.add_repaired_function(network.get_node(inconsistent_node.get_id()).get_function())

            inconsistency.add_repair_set(inconsistent_node.get_id(), repair_set)
            return True
    else:
        # No operation was performed yet, validate if it is a topological change
        if inconsistent_node.has_topological_error():
            return False

    if repair_type == Inconsistencies.CONSISTENT:
        print(f"WARN: Found a consistent node before expected: {inconsistent_node.get_id()}")

    # If a solution was already found, avoid searching for function changes
    if inconsistent_node.is_repaired():
        n_ra_op = inconsistent_node.get_n_add_remove_operations()
        n_fe_op = inconsistent_node.get_n_flip_edges_operations()
        n_op = inconsistent_node.get_n_repair_operations()

        if (n_ra_op == len(added_edges) + len(removed_edges)) and (n_fe_op == len(flipped_edges)) and (n_op == n_ra_op + n_fe_op):
            if configuration["debug"]:
                print("DEBUG: better solution already found. No function search.")
            return False

    # Model is not consistent, and a function change is necessary
    if repair_type == Inconsistencies.DOUBLE_INC:
        if added_edges or removed_edges:
            # If we have a double inconsistency and at least one edge was removed or added,
            # it means that the function was changed to the bottom function, and it's not repairable
            return False

        if configuration["debug"]:
            print(f"DEBUG: searching for non-comparable functions for node {inconsistent_node.get_id()}")

        # Case of double inconsistency
        sol_found = search_non_comparable_functions(inconsistency, inconsistent_node, flipped_edges, added_edges, removed_edges)

        if configuration["debug"]:
            print(f"DEBUG: end searching for non-comparable functions for node {inconsistent_node.get_id()}")

    else:
        if configuration["debug"]:
            print(f"DEBUG: searching for comparable functions for node {inconsistent_node.get_id()}")

        # Case of single inconsistency
        sol_found = search_comparable_functions(inconsistency, inconsistent_node, flipped_edges, added_edges, removed_edges, repair_type == Inconsistencies.SINGLE_INC_GEN)
        if configuration["debug"]:
            print(f"DEBUG: end searching for comparable functions for node {inconsistent_node.get_id()}")

    return sol_found

def n_func_inconsistent_with_label(labeling: Inconsistency_Solution, function: Function) -> int: # TODO what is labeling type?
    result = Inconsistencies.CONSISTENT
    
    # Verify for each profile
    for key, _ in labeling.get_v_label().items():
        ret = n_func_inconsistent_with_label_with_profile(labeling, function, key)
        
        if configuration["debug"]:
            print(f"DEBUG: consistency value: {ret} for node {function.get_node_id()} with function: {function.print_function()}")
        
        if result == Inconsistencies.CONSISTENT:
            result = ret
        else:
            if ret != result and ret != Inconsistencies.CONSISTENT:
                result = Inconsistencies.DOUBLE_INC
                break
    return result

def n_func_inconsistent_with_label_with_profile(labeling: Inconsistency_Solution, function: Function, profile: str) -> int:
    if configuration["debug"]:
        print(f"\n###DEBUG: checking consistency of function: {function.print_function()} of node {function.get_node_id()}\n")

    result = Inconsistencies.CONSISTENT
    profile_map = labeling.get_v_label()[profile]
    time = 0
    last_val = -1
    is_stable_state = len(profile_map) == 1

    while time in profile_map:
        # If it's not a steady state, the following time must exist
        if not is_stable_state and (time + 1) not in profile_map:
            break

        time_map = profile_map[time]

        # Verify if it is an updated node
        if not is_stable_state and update != UpdateType.SYNC:
            updates = labeling.get_updates()[time][profile]
            is_updated = any(update == function.get_node_id() for update in updates)
            if not is_updated:
                time += 1
                continue

        found_sat = False
        n_clauses = function.get_n_clauses() # FIXME how does function already have clauses? should PFH func be initialised? update: i think this is working
        
        for i in range(1, n_clauses + 1):
            is_clause_satisfiable = True
            clauses = function.get_clauses()

            for clause in clauses:
                print(function.bitarray_to_regulators(clause)) # HERE trying to convert the clause to the vars and iterate them to create edges
                print('clause')
                print(clause)
                var = None
                edge = network.get_edge(var, function.get_node_id())
                if edge is not None:
                    # Positive interaction
                    if edge.get_sign() > 0:
                        if time_map[var] == 0:
                            is_clause_satisfiable = False
                            break
                    # Negative interaction
                    else:
                        if time_map[var] > 0:
                            is_clause_satisfiable = False
                            break
                else:
                    print(f"WARN: Missing edge from {var} to {function.get_node_id()}")
                    return False

            if is_clause_satisfiable:
                found_sat = True
                if is_stable_state:
                    if time_map[function.get_node_id()] == 1:
                        return Inconsistencies.CONSISTENT
                    else:
                        return Inconsistencies.SINGLE_INC_PART
                else:
                    if profile_map[time + 1][function.get_node_id()] != 1:
                        if result == Inconsistencies.CONSISTENT or result == Inconsistencies.SINGLE_INC_PART:
                            result = Inconsistencies.SINGLE_INC_PART
                        else:
                            return Inconsistencies.DOUBLE_INC
                    break

        if not found_sat:
            if is_stable_state:
                if n_clauses == 0:
                    return Inconsistencies.CONSISTENT
                else:
                    if time_map[function.get_node_id()] == 0:
                        return Inconsistencies.CONSISTENT
                    return Inconsistencies.SINGLE_INC_GEN
            else:
                if n_clauses == 0:
                    if last_val < 0:
                        last_val = time_map[function.get_node_id()]
                    if profile_map[time + 1][function.get_node_id()] != last_val:
                        return Inconsistencies.DOUBLE_INC
                else:
                    if profile_map[time + 1][function.get_node_id()] != 0:
                        if result == Inconsistencies.CONSISTENT or result == Inconsistencies.SINGLE_INC_GEN:
                            result = Inconsistencies.SINGLE_INC_GEN
                        else:
                            return Inconsistencies.DOUBLE_INC
        time += 1
    return result

def search_comparable_functions(inconsistency: Inconsistency_Solution, inconsistent_node: Inconsistent_Node, flipped_edges: List[Edge], added_edges: List[Edge], removed_edges: List[Edge], generalize: bool):
    sol_found = False
    
    # Get the original function of the inconsistent node
    original_f = network.get_node(inconsistent_node.get_id()).get_function()
    if original_f is None:
        print(f"WARN: Inconsistent node {inconsistent_node.get_id()} without regulatory function.")
        inconsistency.set_impossibility(True)
        return False
    
    if original_f.get_n_regulators() < 2: # TODO why does it return false if n_regulators is < 2?
        return False

    if configuration["debug"]:
        print(f"\tDEBUG: searching for comparable functions of dimension {original_f.get_n_regulators()} going {'down' if generalize else 'up'}")

    # Get the replacement candidates
    function_repaired = False
    repaired_function_level = -1
    t_candidates = original_f.pfh_get_replacements(generalize) # FIXME

    while t_candidates:
        candidate_sol = False
        candidate = t_candidates.pop(0)

        if function_repaired and candidate.get_distance_from_original() > repaired_function_level:
            continue

        if is_func_consistent_with_label(inconsistency, candidate):
            candidate_sol = True
            repair_set = Repair_Set()
            repair_set.add_repaired_function(candidate)
            # Add flipped, added, and removed edges to the repair set
            for edge in flipped_edges:
                repair_set.add_flipped_edge(edge)
            for edge in removed_edges:
                repair_set.remove_edge(edge)
            for edge in added_edges:
                repair_set.add_edge(edge)

            inconsistency.add_repair_set(inconsistent_node.get_id(), repair_set)
            function_repaired = True
            sol_found = True
            repaired_function_level = candidate.get_distance_from_original()

            if not configuration["show_all_functions"]:
                break

        taux_candidates = candidate.get_replacements(generalize) # TODO
        if taux_candidates:
            for taux_candidate in taux_candidates:
                if t_candidates not in taux_candidate:
                    t_candidates.append(taux_candidate)

        if not candidate_sol:
            del candidate
    if not sol_found and configuration["force_optimum"]:
        return search_non_comparable_functions(inconsistency, inconsistent_node, flipped_edges, added_edges, removed_edges)
    return sol_found

def search_non_comparable_functions(inconsistency: Inconsistency_Solution, inconsistent_node: Inconsistent_Node, flipped_edges: List[Edge], added_edges: List[Edge], removed_edges: List[Edge]) -> bool:
    sol_found = False
    candidates = []
    consistent_functions = []

    # To find the best possible functions comparing the levels
    level_compare = configuration["compare_level_function"]
    best_below = []
    best_above = []
    equal_level = []

    # Each function must have a list of replacement candidates and each must be tested until it works
    original_f = network.get_node(inconsistent_node.get_id()).get_function()
    original_map = original_f.get_regulators_map()

    if original_f.get_n_regulators() < 2:
        return False

    if configuration["debug"]:
        print(f"\tDEBUG: searching for non-comparable functions of dimension {original_f.get_n_regulators()}")

    # Construction of new function to start search
    new_f = Function(original_f.get_node_id())
    
    # If the function is in the lower half of the Hasse diagram, start search at the most specific function and generalize
    is_generalize = True
    if level_compare:
        if configuration["debug"]:
            print("DEBUG: Starting half determination")
        is_generalize = is_function_in_bottom_half(original_f)
        if configuration["debug"]:
            print("DEBUG: End half determination")
            print(f"DEBUG: Performing a search going {'up' if is_generalize else 'down'}")

    cindex = 1
    for key in original_map.keys():
        new_f.add_element_clause(cindex, key)
        if not is_generalize:
            cindex += 1

    candidates.append(new_f)

    if configuration["debug"]:
        print(f"DEBUG: Finding functions for double inconsistency in {original_f.print_function()}")

    # Get the possible candidates to replace the inconsistent function
    function_repaired = False
    counter = 0

    while candidates:
        counter += 1
        candidate = candidates.pop(0)
        is_consistent = False

        if candidate in consistent_functions:
            continue

        inc_type = n_func_inconsistent_with_label(inconsistency, candidate)
        if inc_type == Inconsistencies.CONSISTENT:
            is_consistent = True
            consistent_functions.append(candidate)
            if not function_repaired and configuration["debug"]:
                print(f"\tDEBUG: found first function at level {candidate.get_distance_from_original()} {candidate.print_function()}")
            function_repaired = True
            sol_found = True

            if level_compare:
                cmp = original_f.compare_level(candidate)
                if cmp == 0:
                    equal_level.append(candidate)
                    continue
                if is_generalize and cmp < 0 and equal_level:
                    continue
                if not is_generalize and cmp > 0 and equal_level:
                    continue
                if cmp > 0 and not equal_level:
                    if not best_below:
                        best_below.append(candidate)
                    else:
                        rep_cmp = best_below[0].compare_level(candidate)
                        if rep_cmp == 0:
                            best_below.append(candidate)
                        elif rep_cmp < 0:
                            best_below = [candidate]
                    if not is_generalize:
                        continue
                if cmp < 0 and not equal_level:
                    if not best_above:
                        best_above.append(candidate)
                    else:
                        rep_cmp = best_above[0].compare_level(candidate)
                        if rep_cmp == 0:
                            best_above.append(candidate)
                        elif rep_cmp > 0:
                            best_above = [candidate]
                    if is_generalize:
                        continue
        else:
            if candidate.son_consistent:
                del candidate
                continue

            if inc_type == Inconsistencies.DOUBLE_INC or (is_generalize and inc_type == Inconsistencies.SINGLE_INC_PART) or (not is_generalize and inc_type == Inconsistencies.SINGLE_INC_GEN):
                del candidate
                continue

            if level_compare:
                if is_generalize and equal_level and candidate.compare_level(original_f) > 0:
                    del candidate
                    continue
                if not is_generalize and equal_level and candidate.compare_level(original_f) < 0:
                    del candidate
                    continue
                if is_generalize and best_above:
                    if best_above[0].compare_level(candidate) < 0:
                        del candidate
                        continue
                if not is_generalize and best_below:
                    if best_below[0].compare_level(candidate) > 0:
                        del candidate
                        continue

        new_candidates = candidate.get_replacements(is_generalize)
        for new_candidate in new_candidates:
            new_candidate.son_consistent = is_consistent
            if new_candidate not in candidates:
                candidates.append(new_candidate)
        if not is_consistent:
            del candidate

    if configuration["debug"]:
        if function_repaired:
            if level_compare:
                print("\nDEBUG: Printing consistent functions found using level comparison")
                if equal_level:
                    print(f"Looked at {counter} functions. Found {len(consistent_functions)} consistent. Returning {len(equal_level)} functions of same level\n")
                else:
                    print(f"Looked at {counter} functions. Found {len(consistent_functions)} consistent. Returning {len(best_below) + len(best_above)} functions\n")
            else:
                print(f"DEBUG: Looked at {counter} functions. Found {len(consistent_functions)} functions\n")
        else:
            print(f"DEBUG: no consistent functions found - {counter}")

    # Add repair sets to the solution
    if sol_found:
        if level_compare:
            for candidate_set in (equal_level if equal_level else best_below + best_above):
                repair_set = Repair_Set()
                repair_set.add_repaired_function(candidate_set)
                for edge in flipped_edges:
                    repair_set.add_flipped_edge(edge)
                for edge in removed_edges:
                    repair_set.remove_edge(edge)
                for edge in added_edges:
                    repair_set.add_edge(edge)
                inconsistency.add_repair_set(inconsistent_node.get_id(), repair_set)
        else:
            for candidate in consistent_functions:
                repair_set = Repair_Set()
                repair_set.add_repaired_function(candidate)
                for edge in flipped_edges:
                    repair_set.add_flipped_edge(edge)
                for edge in removed_edges:
                    repair_set.remove_edge(edge)
                for edge in added_edges:
                    repair_set.add_edge(edge)
                inconsistency.add_repair_set(inconsistent_node.get_id(), repair_set)
    return sol_found

def is_func_consistent_with_label(labeling: Inconsistency_Solution, function: Function) -> bool:
    for profile in labeling.get_v_label():
        if configuration["debug"]:
            print(f"\n###DEBUG: checking consistency of function: {function.print_function()} of node {function.get_node_id()}")

        profile_map = labeling.get_v_label()[profile]
        time = 0
        is_stable_state = len(profile_map) == 1
        last_val = -1

        while time in profile_map:
            if not is_stable_state and time + 1 not in profile_map:
                break

            time_map = profile_map[time]

            if not is_stable_state and 'update' != 'SYNC':
                updates = labeling.updates_[time][profile]
                if function.get_node_id() not in updates:
                    time += 1
                    continue

            found_sat = False
            n_clauses = function.get_n_clauses()

            for i in range(1, n_clauses + 1):
                is_clause_satisfiable = True
                clause = list(function.get_clauses())[i] # FIXME set is not subscriptable, should it really be a set?

                for item in clause:
                    edge = network.get_edge(item, function.get_node_id())
                    if edge is not None:
                        if edge.get_sign() > 0 and time_map[item] == 0:
                            is_clause_satisfiable = False
                            break
                        elif edge.get_sign() < 0 and time_map[item] > 0:
                            is_clause_satisfiable = False
                            break
                    else:
                        print(f"WARN: Missing edge from {item} to {function.get_node_id()}")
                        return False

                if is_clause_satisfiable:
                    found_sat = True
                    if is_stable_state:
                        return time_map[function.get_node_id()] == 1
                    else:
                        return profile_map[time + 1][function.get_node_id()] == 1

            if not found_sat:
                if is_stable_state:
                    if n_clauses == 0 or time_map[function.get_node_id()] == 0:
                        return True
                    return False
                else:
                    if n_clauses == 0:
                        if last_val < 0:
                            last_val = time_map[function.get_node_id()]
                        return profile_map[time + 1][function.get_node_id()] == last_val
                    return profile_map[time + 1][function.get_node_id()] == 0
            time += 1
    return True

def is_function_in_bottom_half(function: Function) -> bool:
    if configuration["exact_middle_function_determination"]:
        if configuration["debug"]:
            print("DEBUG: Half determination by state")
        return is_function_in_bottom_half_by_state(function)
    
    n = function.get_n_regulators()
    n2 = n // 2
    mid_level = [n2 for _ in range(n)]
    
    return function.compare_level(mid_level) < 0 # TODO understand what compare_level should do and receive

def is_function_in_bottom_half_by_state(function: Function) -> bool:
    reg_map = function.get_regulators_map()
    regulators = function.get_n_regulators()
    entries = int(math.pow(2, regulators))
    n_one = 0
    n_zero = 0

    for entry in range(entries):
        bits = bitarray(bin(entry)[2:].zfill(16))  # Use bitarray to simulate the bitset
        input_map = {}
        bit_index = 0
        for key in reg_map:
            input_map[key] = 1 if bits[bit_index] else 0
            bit_index += 1

        if get_function_value(function, input_map):
            n_one += 1
            if n_one > entries // 2:
                break
        else:
            n_zero += 1
            if n_zero > entries // 2:
                break

    return n_zero > entries // 2

def get_function_value(function: Function, input_map):
    n_clauses = function.get_n_clauses()
    for i in range(1, n_clauses + 1):
        is_clause_satisfiable = True
        clause = function.get_clauses()[i]
        for item in clause:
            edge = network.get_edge(item, function.get_node_id())
            if edge is not None:
                # Positive interaction
                if edge.get_sign() > 0:
                    if input_map[item] == 0:
                        is_clause_satisfiable = False
                        break
                # Negative interaction
                else:
                    if input_map[item] > 0:
                        is_clause_satisfiable = False
                        break
            else:
                print(f"WARN: Missing edge from {item} to {function.get_node_id()}")
                return False
        if is_clause_satisfiable:
            return True
    return False

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
        if not inconsistency.get_has_impossibility():
            if best_solution is None or inconsistency.compare_repairs(best_solution) > 0:
                best_solution = inconsistency
                if configuration["debug"]:
                    print(f"DEBUG: found solution with {best_solution.get_n_topology_changes()} topology changes.")
                if best_solution.get_n_topology_changes() == 0 and not configuration["all_opt"]:
                    break
        else:
            if configuration["debug"]:
                print("DEBUG: Reached an impossibility")

    if best_solution is None:
        print("### It was not possible to repair the model.")
        return

    show_sub_opt = configuration["show_solution_for_each_inconsistency"]

    if configuration["all_opt"]:
        for inconsistency in f_inconsistencies:
            if configuration["debug"]:
                print(f"DEBUG: checking for printing solution with {inconsistency.get_n_topology_changes()} topology changes")
            if not inconsistency.get_has_impossibility() and (inconsistency.compare_repairs(best_solution) >= 0 or show_sub_opt):
                if show_sub_opt and inconsistency.compare_repairs(best_solution) < 0:
                    if verbose < 2:
                        print("+", end="")
                    else:
                        print("(Sub-Optimal Solution)")
                inconsistency.print_solution(verbose, True)
    else:
        best_solution.print_solution(verbose, True)

if __name__ == '__main__':
    network = Network() # Creating a new Network instance

    process_arguments(sys.argv)
    parse = ASPHelper.parse_network(network)
    if parse < 1 and not configuration['ignore_warnings']:
        print('#ABORT:\tModel definition with errors.\n\tCheck documentation for input definition details.')
        sys.exit(-1)

    # Main function that revises the model
    model_revision()