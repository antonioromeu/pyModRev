class Inconsistent_Node:
    def __init__(self, id: str, generalization: bool):
        self.id = id
        self.generalization = generalization
        self.repair_set = []
        self.n_topology_changes = 0
        self.n_repair_operations = 0
        self.n_add_remove_operations = 0
        self.n_flip_edges_operations = 0
        self.repaired = False
        self.topological_error = False
        self.repair_type = 1 if generalization else 2
    
    def get_n_topology_changes(self):
        return self.n_topology_changes

    def get_n_repair_operations(self):
        return self.n_repair_operations

    def get_n_add_remove_operations(self):
        return self.n_add_remove_operations

    def get_n_flip_edges_operations(self):
        return self.n_flip_edges_operations

    def add_repair_set(self, repair_set):
        if not self.repaired:
            self.repaired = True
            self.n_topology_changes = repair_set.get_n_topology_changes()
            self.n_repair_operations = repair_set.get_n_repair_operations()
            self.n_flip_edges_operations = repair_set.get_n_flip_edges_operations()
            self.n_add_remove_operations = repair_set.get_n_add_remove_operations()
        else:
            # If new solutions is worse, ignore
            if (repair_set.get_n_add_remove_operations() > self.n_add_remove_operations):
                return
            if (repair_set.get_n_add_remove_operations() == self.n_add_remove_operations and 
                repair_set.get_n_flip_edges_operations() > self.n_flip_edges_operations):
                return
            if (repair_set.get_n_add_remove_operations() == self.n_add_remove_operations and 
                repair_set.get_n_flip_edges_operations() == self.n_flip_edges_operations and
                repair_set.get_n_repair_operations() > self.n_repair_operations):
                return
            
            # If new solution is better, remove all others before
            # At this point we know that the new repair is at least as good as existing ones
            if repair_set.get_n_repair_operations() < self.n_repair_operations:
                self.repair_set.clear()
                self.n_topology_changes = repair_set.get_n_topology_changes()
                self.n_repair_operations = repair_set.get_n_repair_operations()
                self.n_add_remove_operations = repair_set.get_n_add_remove_operations()
                self.n_flip_edges_operations = repair_set.get_n_flip_edges_operations()

        self.repair_set.append(repair_set)