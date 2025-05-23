"""
This module defines the Inconsistency_Solution class, which represents a
solution to inconsistencies in a network.
The class provides methods to manage and analyze inconsistent nodes, repair
sets, and other related properties.
"""

import json
from typing import Dict
from network.repair_set import Repair_Set
from network.inconsistent_node import Inconsistent_Node
from configuration import configuration


class Inconsistency_Solution:
    """
    Represents a solution to inconsistencies in a network.
    Provides methods to manage inconsistent nodes, repair sets, and other
    properties related to the solution.
    """
    def __init__(self):
        """
        Initializes an empty inconsistency solution with no nodes, repairs,
        or observations.
        """
        # {'i_node_id_1': i_node_1, 'i_node_id_2': i_node_2, ...}
        # Minimum inconsistent node sets of a solution
        self.i_nodes = {}
        # Completed observations that are filled in; if an observation is not
        # complete, ASP fills it in and returns it (ASP tries all combinations)
        self.v_label = {}
        # Only for async, list of updates made for async at each point in time
        self.updates = {}
        # Which of the observations are inconsistent and the respective nodes,
        # used when the process is stopped midway
        self.i_profiles = {}
        self.i_nodes_profiles = {}  # Inconsistent nodes by observation
        self.n_topology_changes = 0
        self.n_ar_operations = 0
        self.n_e_operations = 0
        self.n_repair_operations = 0
        self.has_impossibility = False  # Solution is impossible to repair

    def get_i_nodes(self) -> Dict[str, Inconsistent_Node]:
        """
        Returns all inconsistent nodes in the solution.
        """
        return self.i_nodes

    def get_i_node(self, node_id: str) -> Inconsistent_Node:
        """
        Returns the inconsistent node with the given identifier.
        """
        return self.i_nodes[node_id]

    def get_v_label(self):
        """
        Returns the completed observations filled in by ASP.
        """
        return self.v_label

    def get_updates(self):
        """
        Returns the updates made for asynchronous operations.
        """
        return self.updates

    def get_i_profiles(self):
        """
        Returns the inconsistent profiles and their respective nodes.
        """
        return self.i_profiles

    def get_i_nodes_profiles(self):
        """
        Returns the inconsistent nodes grouped by observation.
        """
        return self.i_nodes_profiles

    def get_n_topology_changes(self) -> int:
        """
        Returns the number of topology changes required for the solution.
        """
        return self.n_topology_changes

    def get_n_ar_operations(self) -> int:
        """
        Returns the number of add/remove operations required for the solution.
        """
        return self.n_ar_operations

    def get_n_e_operations(self) -> int:
        """
        Returns the number of edge flip operations required for the solution.
        """
        return self.n_e_operations

    def get_n_repair_operations(self) -> int:
        """
        Returns the total number of repair operations required for the
        solution.
        """
        return self.n_repair_operations

    def get_has_impossibility(self) -> bool:
        """
        Returns whether the solution is impossible to repair.
        """
        return self.has_impossibility

    def set_impossibility(self, impossibility: bool) -> None:
        """
        Sets whether the solution is impossible to repair.
        """
        self.has_impossibility = impossibility

    def compare_repairs(self, solution: "Inconsistency_Solution") -> int:
        """
        Compares the current solution with another solution to determine which
        is better.
        Returns:
            -1 if provided solution is better than current solution
            0 if provided solution is equal to current solution
            1 if provided solution is weaker than current solution
        """
        if (
            self.n_ar_operations < solution.get_n_ar_operations()
            or self.n_e_operations < solution.get_n_e_operations()
            or self.n_repair_operations < solution.get_n_repair_operations()
        ):
            return 1
        if (
            self.n_ar_operations > solution.get_n_ar_operations()
            or self.n_e_operations > solution.get_n_e_operations()
            or self.n_repair_operations > solution.get_n_repair_operations()
        ):
            return -1
        return 0

    def add_generalization(self, node_id: str) -> None:
        """
        Adds a generalization inconsistency for the node with the given
        identifier.
        """
        if node_id not in self.i_nodes:
            self.i_nodes[node_id] = Inconsistent_Node(node_id, True)
        else:
            i_node = self.i_nodes[node_id]
            if i_node.get_repair_type() != 1:
                if i_node.get_repair_type() == 0:
                    i_node.set_repair_type(1)
                else:
                    i_node.set_repair_type(3)

    def add_particularization(self, node_id: str) -> None:
        """
        Adds a particularization inconsistency for the node with the given
        identifier.
        """
        if node_id not in self.i_nodes:
            self.i_nodes[node_id] = Inconsistent_Node(node_id, False)
        else:
            i_node = self.i_nodes[node_id]
            if i_node.get_repair_type() != 2:
                if i_node.get_repair_type() == 0:
                    i_node.set_repair_type(2)
                else:
                    i_node.set_repair_type(3)

    def add_topological_error(self, node_id: str) -> None:
        """
        Adds a topological error for the node with the given identifier.
        """
        if node_id not in self.i_nodes:
            new_i_node = Inconsistent_Node(node_id, False)
            new_i_node.set_repair_type(0)
            new_i_node.set_topological_error(True)
            self.i_nodes[node_id] = new_i_node
        else:
            self.i_nodes[node_id].set_topological_error(True)

    def add_v_label(self, profile, node_id: str, value, time) -> None:
        """
        Adds a completed observation for the given profile, node, value, and
        time.
        """
        if profile not in self.v_label:
            self.v_label[profile] = {}
        profile_map = self.v_label[profile]
        if time not in profile_map:
            profile_map[time] = {}
        profile_map[time][node_id] = value

    def add_update(self, time, profile, node_id: str) -> None:
        """
        Adds an update for the given time, profile, and node.
        """
        if time not in self.updates:
            self.updates[time] = {}
        time_map = self.updates[time]
        if profile not in time_map:
            time_map[profile] = []
        time_map[profile].append(node_id)

    def add_inconsistent_profile(self, profile, node_id: str) -> None:
        """
        Adds an inconsistent profile for the given profile and node.
        """
        if profile not in self.i_profiles:
            self.i_profiles[profile] = []
        self.i_profiles[profile].append(node_id)
        if node_id not in self.i_nodes_profiles:
            self.i_nodes_profiles[node_id] = []
        self.i_nodes_profiles[node_id].append(profile)

    def add_repair_set(self, node_id: str, repair_set: Repair_Set) -> None:
        """
        Adds a repair set for the node with the given identifier and updates
        repair statistics.
        """
        target = self.i_nodes[node_id]
        if target:
            if not target.repaired:
                self.n_topology_changes += repair_set.get_n_topology_changes()
                self.n_ar_operations += \
                    repair_set.get_n_add_remove_operations()
                self.n_e_operations += \
                    repair_set.get_n_flip_edges_operations()
                self.n_repair_operations += \
                    repair_set.get_n_repair_operations()
            else:
                if repair_set.get_n_add_remove_operations() > \
                        target.get_n_add_remove_operations():
                    return
                if repair_set.get_n_add_remove_operations() == \
                        target.get_n_add_remove_operations() and \
                        repair_set.get_n_flip_edges_operations() > \
                        target.get_n_flip_edges_operations():
                    return
                if repair_set.get_n_add_remove_operations() == \
                        target.get_n_add_remove_operations() and \
                        repair_set.get_n_flip_edges_operations() == \
                        target.get_n_flip_edges_operations() and \
                        repair_set.get_n_repair_operations() > \
                        target.get_n_repair_operations():
                    return
                if repair_set.get_n_repair_operations() < \
                        target.get_n_repair_operations():
                    self.n_topology_changes -= target.get_n_topology_changes()
                    self.n_topology_changes += \
                        repair_set.get_n_topology_changes()
                    self.n_ar_operations -= \
                        target.get_n_add_remove_operations()
                    self.n_ar_operations += \
                        repair_set.get_n_add_remove_operations()
                    self.n_e_operations -= \
                        target.get_n_flip_edges_operations()
                    self.n_e_operations += \
                        repair_set.get_n_flip_edges_operations()
                    self.n_repair_operations -= \
                        target.get_n_repair_operations()
                    self.n_repair_operations += \
                        repair_set.get_n_repair_operations()
            target.add_repair_set(repair_set)

    def print_solution(self, verbose_level: int, print_all) -> None:
        """
        Prints the solution in a human-readable format based on the specified
        verbosity level.
        """
        if verbose_level < 2:
            self.print_parsable_solution(verbose_level)
            return
        if verbose_level == 3:
            self.print_json_solution(print_all)
            return
        print(f"### Found solution with {self.n_repair_operations} repair operations.")
        for i_node in self.i_nodes.values():
            print(f"\tInconsistent node {i_node.get_id()}.")
            i = 1
            for repair in i_node.get_repair_set():
                if print_all:
                    print(f"\t\tRepair #{i}:")
                    i += 1
                for repaired_function in repair.get_repaired_functions():
                    print(f"\t\t\tChange function of {repaired_function.get_node_id()} to {repaired_function.print_function()}.")
                for flipped_edge in repair.get_flipped_edges():
                    print(f"\t\t\tFlip sign of edge ({flipped_edge.get_start_node().get_id()},{flipped_edge.get_end_node().get_id()}).")
                for removed_edge in repair.get_removed_edges():
                    print(f"\t\t\tRemove edge ({removed_edge.get_start_node().get_id()},{removed_edge.get_end_node().get_id()}).")
                for added_edge in repair.get_added_edges():
                    print(f"\t\t\tAdd edge ({added_edge.get_start_node().get_id()},{added_edge.get_end_node().get_id()}) with sign {added_edge.get_sign()}.")
                if not print_all:
                    break
        if configuration['labelling']:
            print("\t### Labelling for this solution:")
            multiple_profiles = configuration['multiple_profiles']
            for profile, times in self.v_label.items():
                if multiple_profiles:
                    print(f"\t\tProfile: {profile}")
                for time, ids in times.items():
                    print(f"\t\t\tTime step: {time}")
                    for _id, value in ids.items():
                        print(f"\t\t\t\t{_id} => {value}")

    def print_parsable_solution(self, verbose_level: int) -> None:
        """
        Prints the solution in a parsable format based on the specified
        verbosity level.
        """
        if verbose_level > 0:
            print("[", end="")
        first_node = True
        for i_node in self.i_nodes.values():
            if not first_node:
                print(";" if verbose_level > 0 else "/", end="")
            first_node = False
            print(i_node.get_id(), end="")
            print(":{" if verbose_level > 0 else "@", end="")
            first_repair = True
            for repair in i_node.get_repair_set():
                if not first_repair:
                    print(";" if verbose_level > 0 else ":", end="")
                first_repair = False
                if verbose_level > 0:
                    print("{", end="")
                first = True
                for added_edge in repair.get_added_edges():
                    if not first:
                        print(";" if verbose_level > 0 else ":", end="")
                    first = False
                    print(f"A:({added_edge.get_start_node().get_id()},{added_edge.get_end_node().get_id()},{added_edge.get_sign()})" if verbose_level > 0
                          else f"A,{added_edge.get_start_node().get_id()},{added_edge.get_end_node().get_id()},{added_edge.get_sign()}", end="")
                for removed_edge in repair.get_removed_edges():
                    if not first:
                        print(";" if verbose_level > 0 else ":", end="")
                    first = False
                    print(f"R:({removed_edge.get_start_node().get_id()},{removed_edge.get_end_node().get_id()})" if verbose_level > 0
                          else f"R,{removed_edge.get_start_node().get_id()},{removed_edge.get_end_node().get_id()}", end="")
                for flipped_edge in repair.get_flipped_edges():
                    if not first:
                        print(";" if verbose_level > 0 else ":", end="")
                    first = False
                    print(f"E:({flipped_edge.get_start_node().get_id()},{flipped_edge.get_end_node().get_id()})" if verbose_level > 0
                          else f"E,{flipped_edge.get_start_node().get_id()},{flipped_edge.get_end_node().get_id()}", end="")
                for repaired_function in repair.get_repaired_functions():
                    if not first:
                        print(";" if verbose_level > 0 else ":", end="")
                    first = False
                    print(f"F:{repaired_function.print_function()}" if verbose_level > 0
                          else f"F,{repaired_function.print_function()}", end="")
                if verbose_level > 0:
                    print("}", end="")
            if verbose_level > 0:
                print("}", end="")
        if verbose_level > 0:
            print("]", end="")
        print()

    def print_json_solution(self, print_all):
        """
        Prints the solution in JSON format.
        """
        result = {
            "solution_repairs": self.n_repair_operations,
            "node_repairs": []
        }

        for node in self.i_nodes.values():
            node_data = {
                "node": node.get_id(),
                "repair_set": []
            }
            first_repair_set = True
            i = 1
            for repair in node.get_repair_set():
                if not first_repair_set:
                    node_data["repair_set"].append({})
                first_repair_set = False

                repair_data = {
                    "repair_id": i,
                    "repairs": []
                }
                i += 1
                # Adding function repairs
                for func in repair.get_repaired_functions():
                    repair_data["repairs"].append({
                        "type": "F",
                        "value": func.print_function()
                    })
                # Adding flipped edges
                for flipped_edge in repair.get_flipped_edges():
                    repair_data["repairs"].append({
                        "type": "E",
                        "value": f"({flipped_edge.get_start_node().get_id()}, {flipped_edge.get_end_node().get_id()})"
                    })
                # Adding removed edges
                for removed_edge in repair.get_removed_edges():
                    repair_data["repairs"].append({
                        "type": "R",
                        "value": f"({removed_edge.get_start_node().get_id()}, {removed_edge.get_end_node().get_id()})"
                    })
                # Adding added edges
                for added_edge in repair.get_added_edges():
                    repair_data["repairs"].append({
                        "type": "A",
                        "value": f"({added_edge.get_start_node().get_id()}, {added_edge.get_end_node().get_id()})",
                        "sign": added_edge.get_sign()
                    })
                node_data["repair_set"].append(repair_data)
                if not print_all:
                    break
            result["node_repairs"].append(node_data)
        print(json.dumps(result, indent=4))

    def print_inconsistency(self, prefix):
        """
        Prints the inconsistency details for the solution.
        """
        print(f'{prefix}"nodes": [', end="")
        first = True
        for i_node in self.i_nodes.values():
            if first:
                first = False
            else:
                print(",", end="")
            print(f'"{i_node.get_id().replace(chr(34), "")}"', end="")
        print("],")
        print(f'{prefix}"profiles": [', end="")
        first = True
        for i_profile in self.i_profiles:
            if first:
                first = False
            else:
                print(",", end="")
            print(f'"{i_profile.replace(chr(34), "")}"', end="")
        print("]")
