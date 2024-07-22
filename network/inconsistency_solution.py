class Inconsistency_Solution:
    def __init__(self):
        self.i_nodes = []
        self.v_label = []
        self.updates = []
        self.i_profiles = []
        self.i_nodes_profiles = []
        self.n_topology_changes = 0
        self.n_ar_operations = 0
        self.n_e_operations = 0
        self.n_repair_operations = 0
        self.has_impossibility = False
    
    def get_i_nodes(self):
        return self.i_nodes

    def get_v_label(self):
        return self.v_label

    def get_updates(self):
        return self.updates

    def get_i_profiles(self):
        return self.i_profiles

    def get_i_nodes_profiles(self):
        return self.i_nodes_profiles

    def get_n_topology_changes(self):
        return self.n_topology_changes

    def get_n_ar_operations(self):
        return self.n_ar_operations

    def get_n_e_operations(self):
        return self.n_e_operations

    def get_n_repair_operations(self):
        return self.n_repair_operations

    def get_has_impossibility(self):
        return self.has_impossibility

    def add_generalization(self, id):
        if id not in self.i_nodes:
            self.i_nodes.append((id, Inconsistent_Node(id, True)))
        else:
            node = self.i_nodes[id]
            if node.repairType != 1:
                if node.repairType == 0:
                    node.repairType = 1
                else:
                    node.repairType = 3

    def add_particularization(self, id):
        if id not in self.i_nodes:
            self.i_nodes[id] = Inconsistent_Node(id, False)
        else:
            node = self.i_nodes[id]
            if node.repairType != 2:
                if node.repairType == 0:
                    node.repairType = 2
                else:
                    node.repairType = 3

    def add_topological_error(self, id):
        if id not in self.i_nodes:
            new_node = Inconsistent_Node(id, False)
            new_node.repairType = 0
            new_node.topologicalError = True
            self.i_nodes[id] = new_node
        else:
            self.i_nodes[id].topologicalError = True

    def add_v_label(self, profile, id, value, time):
        if profile not in self.v_label:
            self.v_label[profile] = {}
        if time not in self.v_label[profile]:
            self.v_label[profile][time] = {}
        self.v_label[profile][time][id] = value

    def add_update(self, time, profile, id):
        if time not in self.updates:
            self.updates[time] = {}
        if profile not in self.updates[time]:
            self.updates[time][profile] = []
        self.updates[time][profile].append(id)

    def add_inconsistent_profile(self, profile, id):
        if profile not in self.i_profiles:
            self.i_profiles[profile] = []
        self.i_profiles[profile].append(id)
        if id not in self.i_nodes_profiles:
            self.i_nodes_profiles[id] = []
        self.i_nodes_profiles[id].append(profile)

    def add_repair_set(self, id, repairSet):
        target = self.i_nodes.get(id)
        if target:
            if not target.repaired:
                self.n_topology_changes += repairSet.get_n_topology_changes()
                self.n_ar_operations += repairSet.getNAddRemoveOperations()
                self.n_e_operations += repairSet.getNFlipEdgesOperations()
                self.n_repair_operations += repairSet.get_n_repair_operations()
            else:
                if repairSet.getNAddRemoveOperations() > target.getNAddRemoveOperations():
                    return
                if repairSet.getNAddRemoveOperations() == target.getNAddRemoveOperations() and repairSet.getNFlipEdgesOperations() > target.getNFlipEdgesOperations():
                    return
                if repairSet.getNAddRemoveOperations() == target.getNAddRemoveOperations() and repairSet.getNFlipEdgesOperations() == target.getNFlipEdgesOperations() and repairSet.get_n_repair_operations() > target.get_n_repair_operations():
                    return
                if repairSet.get_n_repair_operations() < target.get_n_repair_operations():
                    self.n_topology_changes -= target.get_n_topology_changes()
                    self.n_topology_changes += repairSet.get_n_topology_changes()
                    self.n_ar_operations -= target.getNAddRemoveOperations()
                    self.n_ar_operations += repairSet.getNAddRemoveOperations()
                    self.n_e_operations -= target.getNFlipEdgesOperations()
                    self.n_e_operations += repairSet.getNFlipEdgesOperations()
                    self.n_repair_operations -= target.get_n_repair_operations()
                    self.n_repair_operations += repairSet.get_n_repair_operations()
            target.add_repair_set(repairSet)

    def print_solution(self, verboseLevel, printAll):
        if verboseLevel < 2:
            return self.print_parsable_solution(verboseLevel)
        if verboseLevel == 3:
            return self.print_json_solution(printAll)
        print(f"### Found solution with {self.n_repair_operations} repair operations.")
        for i_node in self.i_nodes.values():
            print(f"\tInconsistent node {i_node.id}.")
            i = 1
            for repair in i_node.repairSet:
                if printAll:
                    print(f"\t\tRepair #{i}:")
                    i += 1
                for repairedFunction in repair.repairedFunctions:
                    print(f"\t\t\tChange function of {repairedFunction.getNode()} to {repairedFunction.printFunction()}")
                for flippedEdge in repair.flippedEdges:
                    print(f"\t\t\tFlip sign of edge ({flippedEdge.getStart().id},{flippedEdge.getEnd().id}).")
                for removedEdge in repair.removedEdges:
                    print(f"\t\t\tRemove edge ({removedEdge.getStart().id},{removedEdge.getEnd().id}).")
                for addedEdge in repair.addedEdges:
                    print(f"\t\t\tAdd edge ({addedEdge.getStart().id},{addedEdge.getEnd().id}) with sign {addedEdge.getSign()}.")
                if not printAll:
                    break
        if Configuration.isActive("labelling"):
            print("\t### Labelling for this solution:")
            multipleProfiles = Configuration.isActive("multipleProfiles")
            for profile, times in self.v_label.items():
                if multipleProfiles:
                    print(f"\t\tProfile: {profile}")
                for time, ids in times.items():
                    print(f"\t\t\tTime step: {time}")
                    for id, value in ids.items():
                        print(f"\t\t\t\t{id} => {value}")

    def print_parsable_solution(self, verboseLevel):
        if verboseLevel > 0:
            print("[", end="")
        firstNode = True
        for i_node in self.i_nodes.values():
            if not firstNode:
                print(";" if verboseLevel > 0 else "/", end="")
            firstNode = False
            print(f"{i_node.id}:" if verboseLevel > 0 else "@", end="")
            firstRepair = True
            for repair in i_node.repairSet:
                if not firstRepair:
                    print(";" if verboseLevel > 0 else ":", end="")
                firstRepair = False
                if verboseLevel > 0:
                    print("{", end="")
                first = True
                for addedEdge in repair.addedEdges:
                    if not first:
                        print(";" if verboseLevel > 0 else ":", end="")
                    first = False
                    print(f"A:({addedEdge.getStart().id},{addedEdge.getEnd().id},{addedEdge.getSign()})" if verboseLevel > 0 else f"A,{addedEdge.getStart().id},{addedEdge.getEnd().id},{addedEdge.getSign()}", end="")
                for removedEdge in repair.removedEdges:
                    if not first:
                        print(";" if verboseLevel > 0 else ":", end="")
                    first = False
                    print(f"R:({removedEdge.getStart().id},{removedEdge.getEnd().id})" if verboseLevel > 0 else f"R,{removedEdge.getStart().id},{removedEdge.getEnd().id}", end="")
                for flippedEdge in repair.flippedEdges:
                    if not first:
                        print(";" if verboseLevel > 0 else ":", end="")
                    first = False
                    print(f"E:({flippedEdge.getStart().id},{flippedEdge.getEnd().id})" if verboseLevel > 0 else f"E,{flippedEdge.getStart().id},{flippedEdge.getEnd().id}", end="")
                for repairedFunction in repair.repairedFunctions:
                    if not first:
                        print(";" if verboseLevel > 0 else ":", end="")
                    first = False
                    print(f"F:{repairedFunction.printFunction()}" if verboseLevel > 0 else f"F,{repairedFunction.printFunction()}", end="")
                if verboseLevel > 0:
                    print("}", end="")
            if verboseLevel > 0:
                print("}", end="")
        if verboseLevel > 0:
            print("]", end="")
        print()

    def print_json_solution(self, printAll):
        print("{")
        print(f"\t\"solution_repairs\": {self.n_repair_operations},")
        print("\t\"node_repairs\": [")
        firstNode = True
        for i_node in self.i_nodes.values():
            if not firstNode:
                print(",")
            firstNode = False
            print("\t\t{")
            print(f"\t\t\t\"node\": {i_node.id},")
            print("\t\t\t\"repairs\": [")
            firstRepair = True
            for repair in i_node.repairSet:
                if not firstRepair:
                    print(",")
                firstRepair = False
                print("\t\t\t\t{")
                print("\t\t\t\t\t\"repairs\": [")
                first = True
                for addedEdge in repair.addedEdges:
                    if not first:
                        print(",")
                    first = False
                    print("\t\t\t\t\t\t{")
                    print("\t\t\t\t\t\t\t\"type\": \"add\",")
                    print(f"\t\t\t\t\t\t\t\"from\": {addedEdge.getStart().id},")
                    print(f"\t\t\t\t\t\t\t\"to\": {addedEdge.getEnd().id},")
                    print(f"\t\t\t\t\t\t\t\"sign\": {addedEdge.getSign()}")
                    print("\t\t\t\t\t\t}")
                for removedEdge in repair.removedEdges:
                    if not first:
                        print(",")
                    first = False
                    print("\t\t\t\t\t\t{")
                    print("\t\t\t\t\t\t\t\"type\": \"remove\",")
                    print(f"\t\t\t\t\t\t\t\"from\": {removedEdge.getStart().id},")
                    print(f"\t\t\t\t\t\t\t\"to\": {removedEdge.getEnd().id}")
                    print("\t\t\t\t\t\t}")
                for flippedEdge in repair.flippedEdges:
                    if not first:
                        print(",")
                    first = False
                    print("\t\t\t\t\t\t{")
                    print("\t\t\t\t\t\t\t\"type\": \"flip\",")
                    print(f"\t\t\t\t\t\t\t\"from\": {flippedEdge.getStart().id},")
                    print(f"\t\t\t\t\t\t\t\"to\": {flippedEdge.getEnd().id}")
                    print("\t\t\t\t\t\t}")
                for repairedFunction in repair.repairedFunctions:
                    if not first:
                        print(",")
                    first = False
                    print("\t\t\t\t\t\t{")
                    print("\t\t\t\t\t\t\t\"type\": \"change_function\",")
                    print(f"\t\t\t\t\t\t\t\"function\": \"{repairedFunction.printFunction()}\"")
                    print("\t\t\t\t\t\t}")
                print("\t\t\t\t\t]")
                print("\t\t\t\t}")
                if not printAll:
                    break
            print("\t\t\t]")
            print("\t\t}")
        print("\t]")
        if Configuration.isActive("labelling"):
            print("\t### Labelling for this solution:")
            multipleProfiles = Configuration.isActive("multipleProfiles")
            for profile, times in self.v_label.items():
                if multipleProfiles:
                    print(f"\t\tProfile: {profile}")
                for time, ids in times.items():
                    print(f"\t\t\tTime step: {time}")
                    for id, value in ids.items():
                        print(f"\t\t\t\t{id} => {value}")
        print("}")

    def print_inconsistency(self, prefix):
        print(f"{prefix}\"nodes\": [", end="")
        first = True
        for i_node in self.i_nodes.values():
            if first:
                first = False
            else:
                print(",", end="")
            print(f"\"{Util_h.cleanString(i_node.id)}\"", end="")
        print("],")
        print(f"{prefix}\"profiles\": [", end="")
        first = True
        for i_profile in self.i_profiles.keys():
            if first:
                first = False
            else:
                print(",", end="")
            print(f"\"{Util_h.cleanString(i_profile)}\"", end="")
        print("]")

    # Returns
    # -1 if provided solution is better than current solution
    # 0 if provided solution is equal to current solution
    # 1 if provided solution is weaker than current solution
    def compare_repairs(self, solution):
        if self.n_ar_operations < solution.get_n_ar_operations():
            return 1
        if self.n_ar_operations > solution.get_n_ar_operations():
            return -1
        if self.n_e_operations < solution.get_n_e_operations():
            return 1
        if self.n_e_operations > solution.get_n_e_operations():
            return -1
        if self.n_repair_operations < solution.get_n_repair_operations():
            return 1
        if self.n_repair_operations > solution.get_n_repair_operations():
            return -1
        return 0

    def get_i_node(self, id):
        return self.i_nodes.get(id)