import unittest
from network.network import Network
from network.edge import Edge

class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.network = Network()
    
    def test_get_node(self):
        # Test retrieving an existing node
        node = self.network.add_node('node_1')
        retrieved_node = self.network.get_node('node_1')
        self.assertEqual(retrieved_node, node)

        # Test retrieving a non-existing node
        self.assertIsNone(self.network.get_node('non_existing_node'))
    
    def test_get_nodes(self):
        # Test retrieving an existing node
        self.network.add_node('node_1')
        self.network.add_node('node_2')
        nodes = self.network.get_nodes()
        self.assertEqual(len(nodes), 2)
        self.assertIn('node_1', nodes)
        self.assertIn('node_2', nodes)
    
    def test_get_edge(self):
        # Create mock nodes
        node_1 = self.network.add_node('node_1')
        node_2 = self.network.add_node('node_2')

        # Add an edge between node_1 and node_2
        self.network.add_edge(node_1, node_2, 1)

        # Test getting the edge
        edge = self.network.get_edge('node_1', 'node_2')
        self.assertEqual(edge.get_start_node().get_id(), 'node_1')
        self.assertEqual(edge.get_end_node().get_id(), 'node_2')

        # Test for edge that doesn't exist
        with self.assertRaises(ValueError):
            self.network.get_edge('node_2', 'non_existing_node')

    def test_add_node(self):
        # Test adding a new node   
        node = self.network.add_node('node_1')
        self.assertEqual(node.get_id(), 'node_1')
        self.assertIn('node_1', self.network.get_nodes())
    
    def test_add_edge(self):
        # Create mock nodes
        node_1 = self.network.add_node('node_1')
        node_2 = self.network.add_node('node_2')

        # Add an edge between node1 and node2
        self.network.add_edge(node_1, node_2, 1)

        # Ensure the edge is added in the graph and regulators
        edge = self.network.get_edge('node_1', 'node_2')
        self.assertEqual(edge.get_start_node().get_id(), 'node_1')
        self.assertEqual(edge.get_end_node().get_id(), 'node_2')
        self.assertIn('node_1', self.network.get_graph())
        self.assertIn('node_1', [e.get_start_node().get_id() for e in self.network.get_graph()['node_1']])
        self.assertIn('node_1', self.network.get_regulators()['node_2'])
    
    def test_graph_structure(self):
        # Test getting the graph and regulators before adding nodes and edges
        self.assertEqual(self.network.get_graph(), {})
        self.assertEqual(self.network.get_regulators(), {})

    # def test_remove_edge(self):
    #     self.network.remove_edge(1, 2)
    #     self.assertIsNone(self.network.get_edge(1, 2))
    #     self.assertNotIn(self.edge, self.network.get_edges())

    # def test_remove_edge_instance(self):
    #     edge_to_remove = self.edge
    #     self.network.remove_edge_instance(edge_to_remove)
    #     self.assertIsNone(self.network.get_edge(1, 2))
    #     self.assertNotIn(edge_to_remove, self.network.get_edges())
    
    def test_set_has_ss_obs(self):
        # Test setting and getting has_ss_obs flag
        self.network.set_has_ss_obs(True)
        self.assertTrue(self.network.get_has_ss_obs())

        self.network.set_has_ss_obs(False)
        self.assertFalse(self.network.get_has_ss_obs())

    def test_set_has_ts_obs(self):
        # Test setting and getting has_ts_obs flag
        self.network.set_has_ts_obs(True)
        self.assertTrue(self.network.get_has_ts_obs())

        self.network.set_has_ts_obs(False)
        self.assertFalse(self.network.get_has_ts_obs())

    def test_input_file_network(self):
        # Test setting and getting input file network
        self.network.set_input_file_network('input_file.txt')
        self.assertEqual(self.network.get_input_file_network(), 'input_file.txt')

    def test_observation_files(self):
        # Test adding and getting observation files
        self.network.add_observation_file('observation1.txt')
        self.network.add_observation_file('observation2.txt')

        self.assertIn('observation1.txt', self.network.get_observation_files())
        self.assertIn('observation2.txt', self.network.get_observation_files())
        self.assertEqual(len(self.network.get_observation_files()), 2)

if __name__ == '__main__':
    unittest.main()