import unittest
from node import Node
from edge import Edge

class Network:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.observation_files = []
        self.has_ss_obs = False
        self.has_ts_obs = False

    def __del__(self):
        for node in self.nodes:
            del node

        for edge in self.edges:
            del edge
    
    def get_node(self, id):
        return self.nodes[id]

    def get_nodes(self):
        return self.nodes

    def add_node(self, id): # TODO ask about if ret.second == false
        node = Node(id)
        self.nodes[id] = node
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