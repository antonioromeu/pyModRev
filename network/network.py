import unittest
from network.node import Node
from network.edge import Edge
from typing import Dict, List

class Network:
    def __init__(self) -> None:
        self.nodes = {} # {'node_id_1': node_1, 'node_id_2': node_2, ...}
        self.edges = []
        self.graph = {} # {'node_id_1': ['node_id_2', 'node_id_3'], 'node_id_2': ['node_id_1'], ...}
        self.regulators = {} # Reverse of graph {'node_id_1': ['node_id_2'], 'node_id_2': ['node_id_1'], 'node_id_3': ['node_id_1'], ...}
        self.input_file_network = ''
        self.observation_files = []
        self.has_ss_obs = False
        self.has_ts_obs = False
    
    def get_node(self, id: str) -> Node:
        node = None
        if id in self.nodes.keys():
            node = self.nodes[id]
        return node

    def get_nodes(self) -> Dict[str, Node]:
        return self.nodes
    
    def get_edge(self, start_node_id: str, end_node_id: str) -> Edge:
        for edge in self.edges:
            if edge.get_start_node().get_id() == start_node_id \
                    and edge.get_end_node().get_id() == end_node_id:
                return edge
        raise ValueError('Edge does not exist!')
    
    def get_graph(self) -> Dict[str, List[str]]:
        return self.graph
    
    def get_regulators(self) -> Dict[str, List[str]]:
        return self.regulators

    def get_edges(self) -> List[Edge]:
        return self.edges
    
    def get_input_file_network(self) -> str:
        return self.input_file_network

    def add_node(self, id: str) -> Node:
        node = self.get_node(id)
        if node is None:
            node = Node(id)
            self.nodes[id] = node
            self.graph[id] = []
        return node

    def add_edge(self, start_node: Node, end_node: Node, sign: int) -> None:
        try:
            return self.get_edge(start_node.get_id(), end_node.get_id())
        except ValueError:
            edge = Edge(start_node, end_node, sign)
            self.edges.append(edge)
            self.graph[edge.get_start_node().get_id()].append(edge.get_end_node().get_id())
            if edge.get_end_node().get_id() not in self.regulators.keys():
                self.regulators[edge.get_end_node().get_id()] = [edge.get_start_node().get_id()]
            else:
                self.regulators[edge.get_end_node().get_id()].append(edge.get_start_node().get_id())
            # return edge

    # def add_edge(self, edge: Edge) -> None:
    #     if edge.get_start_node().get_id() in self.graph.keys() and \
    #         edge.get_end_node().get_id() in self.graph[edge.get_start_node().get_id()]:
    #         raise ValueError('Edge already exists!')
    #     self.edges.append(edge)
    #     self.graph[edge.get_start_node().get_id()].append(edge.get_end_node().get_id())
    #     self.regulators[edge.get_end_node().get_id()].append(edge.get_start_node().get_id())
        # return edge

    def remove_edge(self, start_node_id: str, end_node_id: str) -> None:
        self.graph[start_node_id].remove(end_node_id)
        self.regulators[end_node_id].remove(start_node_id)
        for i, edge in enumerate(self.edges):
            if edge.get_start_node().get_id() == start_node_id and \
                    edge.get_end_node().get_id() == end_node_id:
                del self.edges[i]
                return

    def remove_edge(self, edge_to_remove: Edge) -> None:
        self.graph[edge_to_remove.get_start_node().get_id()].remove(edge_to_remove.get_end_node().get_id())
        self.regulators[edge_to_remove.get_end_node().get_id()].remove(edge_to_remove.get_start_node().get_id())
        for i, edge in enumerate(self.edges):
            if edge.get_start_node().get_id() == edge_to_remove.get_start_node().get_id() and \
                    edge.get_end_node().get_id() == edge_to_remove.get_end_node().get_id():
                del self.edges[i]
                return
    
    def set_has_ss_obs(self, has_ss_obs: bool) -> None:
        self.has_ss_obs = has_ss_obs

    def set_has_ts_obs(self, has_ts_obs: bool) -> None:
        self.has_ts_obs = has_ts_obs
    
    def set_input_file_network(self, input_file_netowrk: str) -> None:
        self.input_file_network = input_file_netowrk
    
    def add_observation_file(self, observation_file: str) -> None:
        self.observation_files.append(observation_file)

class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.network = Network()
        self.node1 = self.network.add_node(1)
        self.node2 = self.network.add_node(2)
        self.edge = self.network.add_edge(self.node1, self.node2, 1)

    def test_add_node(self):
        node3 = self.network.add_node(3)
        self.assertEqual(self.network.get_node(3), node3)
        self.assertEqual(node3.get_id(), 3)

    def test_get_node(self):
        self.assertEqual(self.network.get_node(1), self.node1)
        self.assertIsNone(self.network.get_node(3))

    def test_get_nodes(self):
        nodes = self.network.get_nodes()
        self.assertEqual(len(nodes), 2)
        self.assertIn(1, nodes)
        self.assertIn(2, nodes)

    def test_add_edge(self):
        edge = self.network.add_edge(self.node2, self.node1, 0)
        self.assertIn(edge, self.network.get_edges())
        self.assertEqual(edge.get_start_node(), self.node2)
        self.assertEqual(edge.get_end_node(), self.node1)
        self.assertEqual(edge.sign, 0)

    def test_add_edge_instance(self):
        node3 = self.network.add_node(3)
        edge = Edge(self.node2, node3, 1)
        self.network.add_edge_instance(edge)
        self.assertIn(edge, self.network.get_edges())

    def test_get_edge(self):
        self.assertEqual(self.network.get_edge(1, 2), self.edge)
        self.assertIsNone(self.network.get_edge(2, 3))

    def test_get_edges(self):
        self.assertIn(self.edge, self.network.get_edges())

    def test_remove_edge(self):
        self.network.remove_edge(1, 2)
        self.assertIsNone(self.network.get_edge(1, 2))
        self.assertNotIn(self.edge, self.network.get_edges())

    def test_remove_edge_instance(self):
        edge_to_remove = self.edge
        self.network.remove_edge_instance(edge_to_remove)
        self.assertIsNone(self.network.get_edge(1, 2))
        self.assertNotIn(edge_to_remove, self.network.get_edges())

if __name__ == '__main__':
    unittest.main()