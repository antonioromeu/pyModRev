"""
This script analyzes a given network model to determine its consistency.
If inconsistencies are found, it attempts to compute the minimal set of repair
operations needed to restore consistency.
"""

import sys
import math
import os
import importlib
import inspect
from importlib import util
from typing import List, Dict, Tuple
from bitarray import bitarray
from network.network import Network
from network.edge import Edge
from network.function import Function
from network.inconsistency_solution import Inconsistency_Solution
from network.inconsistent_node import Inconsistent_Node
from network.repair_set import Repair_Set
from asp_helper import ASPHelper
from configuration import configuration, UpdateType, Inconsistencies
from updaters.async_updater import AsyncUpdater
from updaters.sync_updater import SyncUpdater
from updaters.steady_state_updater import SteadyStateUpdater
from updaters.complete_updater import CompleteUpdater


def print_help() -> None:
    """
    Print help.
    """
    help_text = f"""
    Model Revision program.
      Given a model and a set of observations, it determines if the model is consistent.
      If not, it computes all the minimum number of repair operations in order to render the model consistent.
    Version: {configuration["version"]}
    Usage:
      main.py [-m] model_file [[-obs] observation_files...] [options]

      options:
        --model,-m <model_file>             Input model file.
        --observations,-obs <obs_files...>  List of observation files.
        --observation-type,-ot <value>      Type of observations in {{ts|ss|both}}. DEFAULT: ts.
                                              ts   - time-series observations
                                              ss   - stable state observations
                                              both - both time-series and stable state observations
        --update,-up <value>                Update mode in {{a|s|c}}. DEFAULT: a.
                                              a - asynchronous update
                                              s - synchronous update
                                              c - complete update
        --check-consistency,-cc             Check the consistency of the model and return without repairing. DEFAULT: false.
        --exhaustive-search                 Force exhaustive search of function repair operations. DEFAULT: false.
        --support,-su                       Support values for each variable.
        --sub-opt                           Show sub-optimal solutions found. DEFAULT: false.
        --verbose,-v <value>                Verbose level {{0,1,2,3}} of output. DEFAULT: 2.
                                              0 - machine style output (minimalistic easily parsable)
                                              1 - machine style output (using sets of sets)
                                              2 - human readable output
                                              3 - JSON format output
        --help,-h                           Print help options.
    """
    print(help_text)


def process_arguments(
        network: Network,
        argv: List[str]) -> None:
    """
    Process command-line arguments and configure network accordingly.
    """
    if len(argv) < 2:
        print_help()
        raise ValueError('Invalid number of arguments')

    obs_type = 0
    last_opt = '-m'
    option_mapping = {
        '--sub-opt': 'show_solution_for_each_inconsistency',
        '--exhaustive-search': 'force_optimum',
        '--check-consistency': 'check_consistency',
        '-cc': 'check_consistency'
    }
    retro_options = {'--steady-state', '--ss'}  # TODO delete
    help_options = {'--help', '-h'}
    model_options = {'--model', '-m'}
    observation_options = {'--observations', '-obs'}
    observation_type_options = {'--observation-type', '-ot'}  # TODO delete
    observation_type_values = {'ts': 0, 'ss': 1, 'both': 2}  # TODO delete
    update_options = {'--update', '-up'}  # TODO delete
    update_values = {'a': UpdateType.ASYNC, 's': UpdateType.SYNC, 'ma': UpdateType.MASYNC}  # TODO delete
    verbose_options = {'--verbose', '-v'}
    debug_options = {'--debug', '-d'}

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == 'main.py':
            i += 1
            continue
        if arg.startswith('-'):
            if arg in option_mapping:
                configuration[option_mapping[arg]] = True
            elif arg in model_options | observation_options | \
                    observation_type_options | update_options | \
                    verbose_options:
                last_opt = arg
            elif arg in retro_options:
                obs_type = 1
            elif arg in help_options:
                print_help()
                sys.exit(0)
            elif arg in debug_options:
                configuration['debug'] = True
            else:
                print_help()
                raise ValueError(f'Invalid option: {arg}')
            i += 1
        else:
            if last_opt in model_options:
                if not network.get_input_file_network():
                    network.set_input_file_network(arg)
                i += 1
            elif last_opt in observation_options:
                while i < len(argv) and not argv[i].startswith('-'):
                    if i + 1 >= len(argv) or argv[i+1].startswith('-'):
                        print_help()
                        raise ValueError("Expected an updater name after the observation file path")
                    obs_path = argv[i]
                    network.add_observation_file(obs_path)
                    updater_name = argv[i + 1]
                    # network.add_updater_name(updater_name)
                    try:
                        if updater_name.lower() != SteadyStateUpdater.__name__.lower():
                            network.set_has_ts_obs(True)
                            if updater_name.lower() == SyncUpdater.__name__.lower():
                                network.add_updater_name('SyncUpdater')
                            elif updater_name.lower() == AsyncUpdater.__name__.lower():
                                network.add_updater_name('AsyncUpdater')
                            elif updater_name.lower() == CompleteUpdater.__name__.lower():
                                network.add_updater_name('CompleteUpdater')
                            else:
                                raise Exception("Unknown non-steady state updater type encountered")
                            if len(network.get_updaters_name()) > 1:
                                raise Exception(f"Conflicting updater types detected: {', '.join(network.get_updaters_name())} cannot coexist.")
                        else:
                            network.set_has_ss_obs(True)
                        updater_dir = os.path.join(os.path.dirname(__file__), "updaters")
                        for filename in os.listdir(updater_dir):
                            if filename.endswith(".py") and filename != os.path.basename(__file__):
                                file_path = os.path.join(updater_dir, filename)
                                classes = load_classes_from_file(file_path)
                                for name, cls in classes.items():
                                    if updater_name.lower() == name.lower():
                                        updater = cls()
                                        network.add_updater(updater)
                                        # network.add_observation_file_with_updater(obs_path, updater)
                        i += 2
                    except ValueError as exc:
                        raise ValueError('Invalid updater') from exc
            elif last_opt in observation_type_options:
                obs_type = observation_type_values.get(arg, None)
                if obs_type is None:
                    print_help()
                    raise ValueError(f'Invalid value for --observation-type: \
                                     {arg}')
                i += 1
            elif last_opt in update_options:
                configuration['update'] = update_values.get(arg, None)
                if configuration['update'] is None:
                    print_help()
                    raise ValueError(f'Invalid value for --update: {arg}')
                i += 1
            elif last_opt in verbose_options:
                try:
                    verbose_level = int(arg)
                    if 0 <= verbose_level <= 3:
                        configuration['verbose'] = verbose_level
                    else:
                        raise ValueError
                except ValueError as exc:
                    print_help()
                    raise ValueError(f'Invalid value for --verbose: {arg}') \
                        from exc
                i += 1
            else:
                i += 1


def load_classes_from_file(file_path: str) -> Dict:
    """
    Dynamically loads classes from a Python file.
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = util.spec_from_file_location(module_name, file_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {name: cls for name, cls in inspect.getmembers(module, inspect.isclass)}


def check_consistency(network: Network) -> Tuple[List[Inconsistency_Solution], int]:
    """
    Check network consistency using ASP solver or alternative method.
    """
    result = []
    optimization = -2
    if configuration['check_asp']:
        # result, optimization = ASPHelper.check_consistency(network, configuration['update'].value)
        result, optimization = ASPHelper.check_consistency(network)
    else:
        pass
    return result, optimization


def print_consistency(
        inconsistencies: List[Inconsistency_Solution],
        optimization: int) -> None:
    """
    Print the consistency status of the network in a structured JSON-like
    format.
    """
    print("{")
    print(f'\t"consistent": {"true" if optimization == 0 else "false,"}')
    if optimization != 0:
        print('\t"inconsistencies": [', end="")
        for i, inconsistency in enumerate(inconsistencies):
            if i > 0:
                print(",", end="")
            print("\n\t\t{", end="")
            inconsistency.print_inconsistency("\t\t\t")
            print("\n\t\t}", end="")
        print("\n\t]")
    print("}")


def repair_inconsistencies(
        network: Network,
        inconsistency: Inconsistency_Solution) -> None:
    """
    This function receives an inconsistent model with a set of nodes to be
    repaired and tries to repair the target nodes making the model consistent
    returning the set of repair operations to be applied.
    """
    for node_id, node in inconsistency.get_i_nodes().items():
        repair_node_consistency(network, inconsistency, node)
        if inconsistency.get_has_impossibility():
            if configuration["debug"]:
                print(f"#Found a node with impossibility - {node_id}")
            return
        if configuration["debug"]:
            print(f"#Found a repair for node - {node_id}")


def repair_node_consistency(
        network: Network,
        inconsistency: Inconsistency_Solution,
        inconsistent_node: Inconsistent_Node) -> None:
    """
    This function repairs a given node and determines all possible solutions
    consider 0 .. N add/remove repair operations, starting with 0 repairs of
    this type
    """
    original_node = network.get_node(inconsistent_node.get_id())
    original_function = original_node.get_function()
    original_regulators = original_function.get_regulators() \
        if original_function is not None \
        else []
    list_edges_remove = []
    list_edges_add = []

    for regulator in original_regulators:
        edge = network.get_edge(regulator, original_function.get_node_id())
        if edge is not None and not edge.get_fixed():
            list_edges_remove.append(edge)

    max_n_remove = len(list_edges_remove)
    max_n_add = len(network.get_nodes()) - max_n_remove

    for node_id, node in network.get_nodes().items():
        is_original_regulator = any(node_id == reg_id for reg_id in
                                    original_regulators)

        if not is_original_regulator:
            new_edge = Edge(node, original_node, 1)
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

            list_add_combination = get_edges_combinations(list_edges_add,
                                                          n_add)
            list_remove_combination = get_edges_combinations(list_edges_remove,
                                                             n_remove)

            for add_combination in list_add_combination:
                for remove_combination in list_remove_combination:
                    is_sol = False

                    # Remove and add edges
                    for edge in remove_combination:
                        if configuration["debug"]:
                            print(f"DEBUG: Remove edge from {edge.get_start_node().get_id()}")
                        network.remove_edge(edge.get_start_node(),
                                            edge.get_end_node())

                    for edge in add_combination:
                        if configuration["debug"]:
                            print(f"DEBUG: Add edge from {edge.get_start_node().get_id()}")
                        network.add_edge(edge.get_start_node(),
                                         edge.get_end_node(), edge.get_sign())

                    # If n_operations > 0, the function must be changed
                    if n_operations > 0:
                        new_function = Function(original_node.get_id())
                        clause_id = 1

                        for regulator in original_regulators:
                            removed = any(regulator ==
                                          edge.get_start_node().get_id()
                                          for edge in remove_combination)
                            if not removed:
                                # TODO try using add_regulator_to_term and only when needed add the clause
                                new_function.add_regulator_to_term(clause_id,
                                                                   regulator)
                                clause_id += 1

                        for edge in add_combination:
                            # TODO try using add_regulator_to_term and only when needed add the clause
                            new_function.add_regulator_to_term(
                                clause_id, edge.get_start_node().get_id())
                            clause_id += 1

                        # TODO does this makes sense? only creating the PFH function if the new function has regulators?
                        if new_function.get_regulators():
                            new_function.create_pfh_function()
                        original_node.add_function(new_function)

                    # Test with edge flips starting with 0 edge flips
                    is_sol = repair_node_consistency_flipping_edges(
                        network, inconsistency, inconsistent_node,
                        add_combination, remove_combination)

                    # Add and remove edges for the original network
                    for edge in remove_combination:
                        network.add_edge(edge.get_start_node(),
                                         edge.get_end_node(), edge.get_sign())

                    for edge in add_combination:
                        network.remove_edge(edge.get_start_node(),
                                            edge.get_end_node())

                    # Restore the original function
                    original_node.add_function(original_function)

                    if is_sol:
                        sol_found = True
                        if not configuration["all_opt"]:
                            if configuration["debug"]:
                                print("DEBUG: No more solutions - all_opt")
                            return
        if sol_found:
            break
    if not sol_found:
        inconsistency.set_impossibility(True)
        print(f"WARN: Not possible to repair node {inconsistent_node.get_id()}")
    return


def repair_node_consistency_flipping_edges(
        network: Network,
        inconsistency: Inconsistency_Solution,
        inconsistent_node: Inconsistent_Node,
        added_edges: List[Edge],
        removed_edges: List[Edge]) -> bool:
    """
    Tries to repair a node's consistency by flipping edges in the network.
    It tests different combinations of edge flips and checks if the
    inconsistency is resolved.
    """
    function = network.get_node(inconsistent_node.get_id()).get_function()
    regulators = function.get_regulators() if function is not None else []
    list_edges = []

    for regulator in regulators:
        edge = network.get_edge(regulator, function.get_node_id())
        if edge is not None and not edge.get_fixed():
            list_edges.append(edge)
    if configuration["debug"]:
        print(f"DEBUG: Searching solution flipping edges for {inconsistent_node.get_id()}")

    sol_found = False
    iterations = len(list_edges)

    # Limit the number of flip edges if the node has already been repaired
    if inconsistent_node.is_repaired():
        iterations = inconsistent_node.get_n_flip_edges_operations()
    for n_edges in range(iterations + 1):
        if configuration["debug"]:
            print(f"DEBUG: Testing with {n_edges} edge flips")

        edges_candidates = get_edges_combinations(list_edges, n_edges)

        # For each set of flipping edges
        for edge_set in edges_candidates:
            # Flip all edges
            for edge in edge_set:
                edge.flip_sign()
                if configuration["debug"]:
                    print(f"DEBUG: Flip edge from {edge.get_start_node().get_id()}")
            is_sol = repair_node_consistency_functions(network, inconsistency,
                                                       inconsistent_node,
                                                       edge_set, added_edges,
                                                       removed_edges)
            # Put network back to normal by flipping edges back
            for edge in edge_set:
                edge.flip_sign()
                if configuration["debug"]:
                    print(f"DEBUG: Return flip edge from {edge.get_start_node().get_id()}")
            if is_sol:
                if configuration["debug"]:
                    print("DEBUG: Is solution by flipping edges")
                sol_found = True
                if not configuration["all_opt"]:
                    if configuration["debug"]:
                        print("DEBUG: No more solutions - all_opt")
                    return True
        if sol_found:
            if configuration["debug"]:
                print(f"DEBUG: Ready to end with {n_edges} edges flipped")
            break

    return sol_found


def repair_node_consistency_functions(
        network: Network,
        inconsistency: Inconsistency_Solution,
        inconsistent_node: Inconsistent_Node,
        flipped_edges: List[Edge],
        added_edges: List[Edge],
        removed_edges: List[Edge]) -> bool:
    """
    Repairs a node's function if needed by checking for consistency after
    topological changes, and if necessary, searches for a function change to
    resolve inconsistencies.
    """
    sol_found = False
    repair_type = inconsistent_node.get_repair_type()

    # If any topological operation was performed, validate if the model
    # became consistent
    if flipped_edges or added_edges or removed_edges:
        repair_type = n_func_inconsistent_with_label(
            network, inconsistency,
            network.get_node(inconsistent_node.get_id()).get_function())
        if repair_type == Inconsistencies.CONSISTENT.value:
            if configuration["debug"]:
                print("DEBUG: Node consistent with only topological changes")

            repair_set = Repair_Set()

            for edge in flipped_edges:
                repair_set.add_flipped_edge(edge)

            # Add and remove edges in the solution repair set
            for edge in removed_edges:
                repair_set.remove_edge(edge)

            for edge in added_edges:
                repair_set.add_edge(edge)

            if added_edges or removed_edges:
                repair_set.add_repaired_function(network.get_node(
                    inconsistent_node.get_id()).get_function())

            inconsistency.add_repair_set(inconsistent_node.get_id(),
                                         repair_set)
            return True
    else:
        # No operation was performed yet, validate if it is a topological
        # change
        if inconsistent_node.has_topological_error():
            return False

    if repair_type == Inconsistencies.CONSISTENT.value:
        print(f"WARN: Found a consistent node before expected: {inconsistent_node.get_id()}")

    # If a solution was already found, avoid searching for function changes
    if inconsistent_node.is_repaired():
        n_ra_op = inconsistent_node.get_n_add_remove_operations()
        n_fe_op = inconsistent_node.get_n_flip_edges_operations()
        n_op = inconsistent_node.get_n_repair_operations()

        if (n_ra_op == len(added_edges) + len(removed_edges)) and (
                n_fe_op == len(flipped_edges)) and (n_op == n_ra_op + n_fe_op):
            if configuration["debug"]:
                print("DEBUG: Better solution already found. No function search.")
            return False

    # Model is not consistent and a function change is necessary
    if repair_type == Inconsistencies.DOUBLE_INC.value:
        if added_edges or removed_edges:
            # If we have a double inconsistency and at least one edge was
            # removed or added, it means that the function was changed to the
            # bottom function, and it's not repairable
            return False

        if configuration["debug"]:
            print(f"DEBUG: Searching for non-comparable functions for node {inconsistent_node.get_id()}")

        # Case of double inconsistency
        sol_found = search_non_comparable_functions(network, inconsistency,
                                                    inconsistent_node,
                                                    flipped_edges, added_edges,
                                                    removed_edges)

        if configuration["debug"]:
            print(f"DEBUG: End searching for non-comparable functions for node {inconsistent_node.get_id()}")

    else:
        if configuration["debug"]:
            print(f"DEBUG: Searching for comparable functions for node {inconsistent_node.get_id()}")

        # Case of single inconsistency
        sol_found = search_comparable_functions(
            network, inconsistency, inconsistent_node, flipped_edges,
            added_edges, removed_edges,
            repair_type == Inconsistencies.SINGLE_INC_GEN.value)
        if configuration["debug"]:
            print(f"DEBUG: End searching for comparable functions for node {inconsistent_node.get_id()}")

    return sol_found


def n_func_inconsistent_with_label(
        network: Network,
        labeling: Inconsistency_Solution,
        function: Function) -> int:
    """
    Checks the consistency of a function against a labeling. It verifies each
    profile and returns the consistency status (consistent, inconsistent, or
    double inconsistency).
    """
    result = Inconsistencies.CONSISTENT.value
    for key in labeling.get_v_label():
        ret = n_func_inconsistent_with_label_with_profile(network, labeling, function, key)
        if configuration["debug"]:
            print(f"DEBUG: Consistency value: {ret} for node {function.get_node_id()} with function: {function.print_function()}")
        if result == Inconsistencies.CONSISTENT.value:
            result = ret
        else:
            if ret not in (result, Inconsistencies.CONSISTENT.value):
                result = Inconsistencies.DOUBLE_INC.value
                break
    return result


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
    if len(labeling.get_v_label()[profile]) == 1 and network.get_has_ss_obs():
        return SteadyStateUpdater.n_func_inconsistent_with_label_with_profile(network, labeling, function, profile)
    for updater in network.get_updaters():
        if len(labeling.get_v_label()[profile]) != 1 and updater.__class__.__name__.lower() != SteadyStateUpdater.__name__.lower():
            return updater.n_func_inconsistent_with_label_with_profile(network, labeling, function, profile)
    # result = 0
    # if network.get_has_ss_obs():
    #     result = SteadyStateUpdater.n_func_inconsistent_with_label_with_profile(network, labeling, function, profile)
    # if result == 0 and network.get_updaters():
    #     updater = network.get_updaters().pop()
    #     result = updater.n_func_inconsistent_with_label_with_profile(network, labeling, function, profile)
    # return result

    # results = []
    # for _, updater in network.get_observation_files_with_updater():
    #     result = updater.n_func_inconsistent_with_label_with_profile(network, labeling, function, profile)
    #     results.append(result)
    # return max(results) if results else 0
    # updater = labeling.get_updater()
    # return updater.n_func_inconsistent_with_label_with_profile(network, labeling, function, profile)


# def n_func_inconsistent_with_label_with_profile(
#         network: Network, labeling: Inconsistency_Solution, function: Function,
#         profile: str) -> int:
#     """
#     Checks the consistency of a function with a specific profile in a given
#     labeling. It evaluates the function's clauses over time and returns the
#     consistency status (consistent, single inconsistency, or double
#     inconsistency) based on the profile.
#     """
#     if configuration["debug"]:
#         print(f"\n###DEBUG: Checking consistency of function: {function.print_function()} of node {function.get_node_id()}")

#     result = Inconsistencies.CONSISTENT.value
#     profile_map = labeling.get_v_label()[profile]
#     time = 0
#     last_val = -1
#     is_stable_state = len(profile_map) == 1

#     while time in profile_map:
#         # If it's not a steady state, the following time must exist
#         if not is_stable_state and (time + 1) not in profile_map:
#             break

#         time_map = profile_map[time]
#         # Verify if it is an updated node
#         if not is_stable_state and configuration["update"] != UpdateType.SYNC:
#             updates = labeling.get_updates()[time][profile]
#             is_updated = any(update == function.get_node_id()
#                              for update in updates)
#             if not is_updated:
#                 time += 1
#                 continue

#         found_sat = False
#         n_clauses = function.get_n_clauses()

#         if n_clauses:
#             clauses = function.get_clauses()
#             for clause in clauses:
#                 is_clause_satisfiable = True
#                 _vars = function.bitarray_to_regulators(clause)
#                 for var in _vars:
#                     edge = network.get_edge(var, function.get_node_id())
#                     if edge is not None:
#                         # Determine if clause is satisfiable based on edge sign
#                         if (edge.get_sign() > 0) == (time_map[var] == 0):
#                             is_clause_satisfiable = False
#                             # Stop checking if clause is already unsatisfiable
#                             break
#                     else:
#                         print(f"WARN: Missing edge from {var} to {function.get_node_id()}")
#                         return False

#                 # Evaluate satisfaction status of the clause
#                 if is_clause_satisfiable:
#                     found_sat = True
#                     if is_stable_state:
#                         if time_map[function.get_node_id()] == 1:
#                             return Inconsistencies.CONSISTENT.value
#                         return Inconsistencies.SINGLE_INC_PART.value
#                     if profile_map[time + 1][function.get_node_id()] != 1:
#                         if result in (Inconsistencies.CONSISTENT.value,
#                                       Inconsistencies.SINGLE_INC_PART.value):
#                             result = Inconsistencies.SINGLE_INC_PART.value
#                         else:
#                             return Inconsistencies.DOUBLE_INC.value
#                     # Stop if one satisfiable clause is found
#                     break

#         if not found_sat:
#             if is_stable_state:
#                 if n_clauses == 0:
#                     return Inconsistencies.CONSISTENT.value
#                 if time_map[function.get_node_id()] == 0:
#                     return Inconsistencies.CONSISTENT.value
#                 return Inconsistencies.SINGLE_INC_GEN.value
#             if n_clauses == 0:
#                 if last_val < 0:
#                     last_val = time_map[function.get_node_id()]
#                 if profile_map[time + 1][function.get_node_id()] != \
#                         last_val:
#                     return Inconsistencies.DOUBLE_INC.value
#             else:
#                 if profile_map[time + 1][function.get_node_id()] != 0:
#                     if result in (Inconsistencies.CONSISTENT.value,
#                                   Inconsistencies.SINGLE_INC_GEN.value):
#                         result = Inconsistencies.SINGLE_INC_GEN.value
#                     else:
#                         return Inconsistencies.DOUBLE_INC.value
#         time += 1
#     return result


def search_comparable_functions(
        network: Network,
        inconsistency: Inconsistency_Solution,
        inconsistent_node: Inconsistent_Node,
        flipped_edges: List[Edge],
        added_edges: List[Edge],
        removed_edges: List[Edge],
        generalize: bool) -> bool:
    """
    Searches for comparable functions that can repair the inconsistency of a
    node. It evaluates potential replacement functions and applies the
    necessary edges to resolve the inconsistency.
    """
    sol_found = False
    original_f = network.get_node(inconsistent_node.get_id()).get_function()

    if original_f is None:
        print(f"WARN: Inconsistent node {inconsistent_node.get_id()} without regulatory function")
        inconsistency.set_impossibility(True)
        return False

    if original_f.get_n_regulators() < 2:
        return False

    if configuration["debug"]:
        print(f"\tDEBUG: Searching for comparable functions of dimension {original_f.get_n_regulators()} going {'down' if generalize else 'up'}")

    # Get the replacement candidates
    function_repaired = False
    repaired_function_level = -1
    t_candidates = original_f.pfh_get_replacements(generalize)

    while t_candidates:
        candidate_sol = False
        candidate = t_candidates.pop(0)
        if function_repaired and candidate.get_distance_from_original() > \
                repaired_function_level:
            continue
        if is_func_consistent_with_label(network, inconsistency, candidate):
            candidate_sol = True
            repair_set = Repair_Set()
            repair_set.add_repaired_function(candidate)
            for edge in flipped_edges:
                repair_set.add_flipped_edge(edge)
            for edge in removed_edges:
                repair_set.remove_edge(edge)
            for edge in added_edges:
                repair_set.add_edge(edge)
            inconsistency.add_repair_set(inconsistent_node.get_id(),
                                         repair_set)
            function_repaired = True
            sol_found = True
            repaired_function_level = candidate.get_distance_from_original()

            if not configuration["show_all_functions"]:
                break

        taux_candidates = candidate.pfh_get_replacements(generalize)
        if taux_candidates:
            for taux_candidate in taux_candidates:
                if not is_in(taux_candidate, t_candidates):
                    t_candidates.append(taux_candidate)

        if not candidate_sol:
            del candidate
    if not sol_found and configuration["force_optimum"]:
        return search_non_comparable_functions(network, inconsistency,
                                               inconsistent_node,
                                               flipped_edges, added_edges,
                                               removed_edges)
    return sol_found


def search_non_comparable_functions(
        network: Network,
        inconsistency: Inconsistency_Solution,
        inconsistent_node: Inconsistent_Node,
        flipped_edges: List[Edge],
        added_edges: List[Edge],
        removed_edges: List[Edge]) -> bool:
    """
    Searches for non-comparable functions to resolve inconsistencies in the
    given network. Attempts to replace an inconsistent function with a
    consistent alternative.
    """
    sol_found, function_repaired = False, False
    candidates, consistent_functions = [], []
    best_below, best_above, equal_level = [], [], []
    level_compare = configuration["compare_level_function"]

    # Each function must have a list of replacement candidates and each must
    # be tested until it works
    original_f = network.get_node(inconsistent_node.get_id()).get_function()
    original_map = original_f.get_regulators_by_term()

    if original_f.get_n_regulators() < 2:
        return False

    if configuration["debug"]:
        print(f"\tDEBUG: Searching for non-comparable functions of dimension {original_f.get_n_regulators()}")

    # Construction of new function to start search
    # TODO is missing the copy of the other attributes, might lead to error
    new_f = Function(original_f.get_node_id())

    # If the function is in the lower half of the Hasse diagram, start search
    # at the most specific function and generalize
    is_generalize = True
    if level_compare:
        if configuration["debug"]:
            print("DEBUG: Starting half determination")
        is_generalize = is_function_in_bottom_half(network, original_f)
        if configuration["debug"]:
            print("DEBUG: End half determination")
            print(f"DEBUG: Performing a search going {'up' if is_generalize else 'down'}")

    cindex = 1
    for _, _vars in original_map.items():
        for var in _vars:
            new_f.add_regulator_to_term(cindex, var)
            if not is_generalize:
                cindex += 1

    candidates.append(new_f)

    if configuration["debug"]:
        print(f"DEBUG: Finding functions for double inconsistency in {original_f.print_function()}")

    counter = 0
    while candidates:
        counter += 1
        candidate = candidates.pop(0)
        is_consistent = False

        if is_in(candidate, consistent_functions):
            continue

        inc_type = n_func_inconsistent_with_label(network, inconsistency,
                                                  candidate)
        if inc_type == Inconsistencies.CONSISTENT.value:
            is_consistent = True
            consistent_functions.append(candidate)
            if not function_repaired and configuration["debug"]:
                print(f"\tDEBUG: Found first function at level {candidate.get_distance_from_original()} {candidate.print_function()}")
            function_repaired, sol_found = True, True
            if level_compare:
                cmp = original_f.compare_level(candidate)
                if cmp == 0:
                    equal_level.append(candidate)
                    continue
                if (is_generalize and cmp < 0 and equal_level) \
                        or (not is_generalize and cmp > 0 and equal_level):
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

            if inc_type == Inconsistencies.DOUBLE_INC.value or \
                    (is_generalize
                     and inc_type == Inconsistencies.SINGLE_INC_PART.value) \
                    or (not is_generalize
                        and inc_type == Inconsistencies.SINGLE_INC_GEN.value):
                del candidate
                continue

            if level_compare:
                if is_generalize and equal_level \
                        and candidate.compare_level(original_f) > 0:
                    del candidate
                    continue
                if not is_generalize and equal_level \
                        and candidate.compare_level(original_f) < 0:
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
            new_candidate.set_son_consistent(is_consistent)
            if not is_in(new_candidate, candidates):
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
            print(f"DEBUG: No consistent functions found - {counter}")

    # Add repair sets to the solution
    if sol_found:
        if level_compare:
            for candidate_set in (equal_level if equal_level else best_below +
                                  best_above):
                repair_set = Repair_Set()
                repair_set.add_repaired_function(candidate_set)
                for edge in flipped_edges:
                    repair_set.add_flipped_edge(edge)
                for edge in removed_edges:
                    repair_set.remove_edge(edge)
                for edge in added_edges:
                    repair_set.add_edge(edge)
                inconsistency.add_repair_set(inconsistent_node.get_id(),
                                             repair_set)
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
                inconsistency.add_repair_set(inconsistent_node.get_id(),
                                             repair_set)
    return sol_found


# def is_func_consistent_with_label_with_profile(
#         network: Network, labeling: Inconsistency_Solution, function: Function,
#         profile: str) -> bool:
#     """
#     Evaluates whether the function's regulatory logic aligns with the expected
#     time-dependent behavior of the network, ensuring that the function's
#     clauses are satisfied at each time step. It considers both stable states
#     and dynamic updates based on the profile's labeling.
#     """
#     if configuration["debug"]:
#         print(f"\n###DEBUG: Checking consistency of function: {function.print_function()} of node {function.get_node_id()}")

#     profile_map = labeling.get_v_label()[profile]
#     time = 0
#     is_stable_state = len(profile_map) == 1
#     last_val = -1

#     while time in profile_map:
#         if not is_stable_state and time + 1 not in profile_map:
#             break

#         time_map = profile_map[time]
#         if not is_stable_state and configuration["update"] != UpdateType.SYNC:
#             updates = labeling.get_updates()[time][profile]
#             is_updated = any(update == function.get_node_id()
#                              for update in updates)
#             if not is_updated:
#                 time += 1
#                 continue

#         found_sat = False
#         n_clauses = function.get_n_clauses()

#         if n_clauses:
#             clauses = function.get_clauses()
#             for clause in clauses:
#                 is_clause_satisfiable = True
#                 _vars = function.bitarray_to_regulators(clause)
#                 for var in _vars:
#                     edge = network.get_edge(var, function.get_node_id())
#                     if edge is not None:
#                         # Determine if clause is satisfiable based on edge sign
#                         if (edge.get_sign() > 0) == (time_map[var] == 0):
#                             is_clause_satisfiable = False
#                             # Stop checking if clause is already unsatisfiable
#                             break
#                     else:
#                         print(f"WARN: Missing edge from {var} to {function.get_node_id()}")
#                         return False
#                 if is_clause_satisfiable:
#                     found_sat = True
#                     if is_stable_state:
#                         return time_map[function.get_node_id()] == 1
#                     if profile_map[time + 1][function.get_node_id()] != 1:
#                         return False
#                     break

#         if not found_sat:
#             if is_stable_state:
#                 return n_clauses == 0 or time_map[function.get_node_id()] == 0
#             if n_clauses == 0:
#                 if last_val < 0:
#                     last_val = time_map[function.get_node_id()]
#                 if profile_map[time + 1][function.get_node_id()] != \
#                         last_val:
#                     return False
#             else:
#                 if profile_map[time + 1][function.get_node_id()] != 0:
#                     return False
#         time += 1
#     return True


def is_func_consistent_with_label(
        network: Network,
        labeling: Inconsistency_Solution,
        function: Function) -> bool:
    """
    Checks if a function is consistent with a labeling across all profiles.
    """
    return all(
        is_func_consistent_with_label_with_profile(network, labeling, function, profile)
        for profile in labeling.get_v_label()
    )


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
    if len(labeling.get_v_label()[profile]) == 1 and network.get_has_ss_obs():
        return SteadyStateUpdater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)
    for updater in network.get_updaters():
        if len(labeling.get_v_label()[profile]) != 1 and updater.__class__.__name__.lower() != SteadyStateUpdater.__name__.lower():
            return updater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)
    # result = False
    # if network.get_has_ss_obs():
    #     result = SteadyStateUpdater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)
    # if network.get_has_ts_obs() and not result and network.get_updaters():
    #     updater = network.get_updaters().pop()
    #     result = updater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)
    # return result
    # # print(updater)
    # return all(
    #     updater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)
    #     for _, updater in network.get_observation_files_with_updater()
    # )
    # non_steady_results = []
    # steady_results = []
    # for _, updater in network.get_observation_files_with_updater():
    #     print(updater)
    #     if isinstance(updater, SteadyStateUpdater):
    #         print(updater)
    #         steady_results.append(
    #             updater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)
    #         )
    #     else:
    #         non_steady_results.append(
    #             updater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)
    #         )
    # If there is at least one non-steady updater, its result must be True,
    # and also all steady state updaters must return True.
    # non_steady_consistent = all(non_steady_results) if non_steady_results else True
    # steady_consistent = all(steady_results) if steady_results else True
    # return non_steady_consistent and steady_consistent
    # return Updater.is_func_consistent_with_label_with_profile(network, labeling, function, profile)


def is_function_in_bottom_half(
        network: Network,
        function: Function) -> bool:
    """
    Determines if a function is in the bottom half based on its regulators.
    If exact middle determination is enabled, it uses a different method.
    """
    if configuration["exact_middle_function_determination"]:
        if configuration["debug"]:
            print("DEBUG: Half determination by state")
        return is_function_in_bottom_half_by_state(network, function)
    n = function.get_n_regulators()
    n2 = n // 2
    mid_level = [n2 for _ in range(n)]
    return function.compare_level_list(mid_level) < 0


def is_function_in_bottom_half_by_state(
        network: Network,
        function: Function) -> bool:
    """
    Determines if a function is in the bottom half based on its state by
    evaluating its output across all possible input combinations.
    """
    regulators = function.get_regulators()
    n_regulators = function.get_n_regulators()
    entries = int(math.pow(2, n_regulators))
    n_one = 0
    n_zero = 0
    for entry in range(entries):
        # Use bitarray to simulate the bitset, little-endian order
        bits = bitarray(bin(entry)[2:].zfill(16)[::-1])
        input_map = {}
        bit_index = 0
        for regulator in regulators:
            input_map[regulator] = 1 if bits[bit_index] else 0
            bit_index += 1
        if get_function_value(network, function, input_map):
            n_one += 1
            if n_one > (entries // 2):
                break
        else:
            n_zero += 1
            if n_zero > (entries // 2):
                break
    return n_zero > (entries // 2)


def get_function_value(
        network: Network,
        function: Function,
        input_map: Dict[str, int]):
    """
    Evaluates the value of a function based on the given input map. It checks
    the satisfaction of the function's clauses.
    """
    n_clauses = function.get_n_clauses()
    if n_clauses:
        clauses = function.get_clauses()
        for clause in clauses:
            is_clause_satisfiable = True
            _vars = function.bitarray_to_regulators(clause)
            for var in _vars:
                edge = network.get_edge(var, function.get_node_id())
                if edge is not None:
                    # Determine if clause is satisfiable based on edge sign
                    if (edge.get_sign() > 0) == (input_map[var] == 0):
                        is_clause_satisfiable = False
                        # Stop checking if clause is already unsatisfiable
                        break
                else:
                    print(f"WARN: Missing edge from {var} to {function.get_node_id()}")
                    return False
            if is_clause_satisfiable:
                return True
    return False


def get_edges_combinations(
        edges: List[Edge],
        n: int,
        index_start: int = 0) -> List[List[Edge]]:
    """
    Generate all possible combinations of edges with specified size.
    """
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


def model_revision(network: Network) -> None:
    """
    Analyze and revise a given network model for consistency.
    Procedure:
        1st - tries to repair functions
        2nd - tries to flip the sign of the edges
        3rd - tries to add or remove edges
    """
    optimization = -2
    f_inconsistencies, optimization = check_consistency(network)
    if configuration["check_consistency"]:
        print_consistency(f_inconsistencies, optimization)
        return

    if optimization < 0:
        print("ERROR: It is not possible to repair this network for now.")
        print("This may occur if there is at least one node for which from the same input two different outputs are expected (non-deterministic function).")
        return

    if optimization == 0:
        if configuration["verbose"] == 3:
            print_consistency(f_inconsistencies, optimization)
            return
        print("This network is consistent!")
        return

    if configuration["debug"]:
        print(f"Found {len(f_inconsistencies)} solution(s) with {len(f_inconsistencies[0].get_i_nodes())} inconsistent node(s)")

    # At this point we have an inconsistent network with node candidates
    # to be repaired
    best_solution = None
    for inconsistency in f_inconsistencies:
        repair_inconsistencies(network, inconsistency)

        # Check for valid solution
        if not inconsistency.get_has_impossibility():
            if best_solution is None \
                    or inconsistency.compare_repairs(best_solution) > 0:
                best_solution = inconsistency
                if configuration["debug"]:
                    print(f"DEBUG: Found a solution with {best_solution.get_n_topology_changes()} topology changes")
                if best_solution.get_n_topology_changes() == 0 and not \
                        configuration["all_opt"]:
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
                print(f"DEBUG: Checking for printing solution with {inconsistency.get_n_topology_changes()} topology changes")
            if not inconsistency.get_has_impossibility() \
                    and (inconsistency.compare_repairs(best_solution) >= 0
                         or show_sub_opt):
                if show_sub_opt \
                        and inconsistency.compare_repairs(best_solution) < 0:
                    if configuration["verbose"] < 2:
                        print("+", end="")
                    else:
                        print("(Sub-Optimal Solution)")
                inconsistency.print_solution(configuration["verbose"], True)
    else:
        best_solution.print_solution(configuration["verbose"], True)


def is_in(
        item: Function,
        lst: List[Function]) -> bool:
    """
    Checks if a function is present in a list by comparing it to each element.
    """
    return any(item.is_equal(aux) for aux in lst)


if __name__ == '__main__':
    network = Network()
    process_arguments(network, sys.argv)
    parse = ASPHelper.parse_network(network)
    if parse < 1 and not configuration['ignore_warnings']:
        print('#ABORT:\tModel definition with errors.\n\tCheck documentation for input definition details.')
        sys.exit(-1)
    model_revision(network)
