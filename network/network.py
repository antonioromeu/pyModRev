from node import Node
from edge import Edge

class Network:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.observation_files = []
        self.has_ss_obs = False
        self.has_ts_obs = False

    def __del__(self):
        for node in self.nodes:
            del node

        for edge in self.edges:
            del edge
    
    def get_node(self, id): # TODO
        return node for node in self.nodes if node[0] == id

    def get_nodes(self):
        return self.nodes

    def add_node(self, id): # TODO
        node = Node(id)
        self.nodes.append((id, node))
        ret = self.nodes.set_default(id, node)
        if ret is not node:
            del node
            return ret
        return node

    def get_edge(self, start_node_id, end_node_id):
        for edge in self.edges:
            if edge.get_start_node().get_id() == start_node_id and edge.get_end_node().get_id == end_node_id:
                return edge
        return None
    
    def get_edges(self):
        return self.edges

    def add_edge(self, start_node, end_node, sign):
        edge = Edge(start_node, end_node, sign)
        self.edges.append(edge)
        return edge

    def add_edge(self, edge_to_add):
        self.edges.append(edge_to_add)

    def remove_edge(self, start_node_id, end_node_id):
        for i, edge in enumerate(self.edges):
            if edge.get_start_node().get_id() == start_node_id and edge.get_end_node().get_id() == end_node_id:
                del self.edges[i]
                return

    def remove_edge(self, edge_to_remove):
         for i, edge in enumerate(self.edges):
            if (edge.get_start_node().get_id() == edge_to_remove.get_start_node().get_id()) 
                    and (edge.get_end_node().get_id() == edge_to_remove.get_end_node().get_id()):
                del self.edges[i]
                return