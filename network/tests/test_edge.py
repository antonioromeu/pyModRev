import unittest
from network.node import Node
from network.edge import Edge

class TestEdge(unittest.TestCase):
    def setUp(self):
        self.node_1 = Node('node_1')
        self.node_2 = Node('node_2')
        self.edge = Edge(self.node_1, self.node_2, 1)
    
    def test_initialization(self):
        # Test that the edge initializes correctly
        self.assertEqual(self.edge.get_start_node(), self.node_1)
        self.assertEqual(self.edge.get_end_node(), self.node_2)
        self.assertEqual(self.edge.get_sign(), 1)
        self.assertFalse(self.edge.get_fixed())

    def test_flip_sign(self):
        # Test flipping the sign
        self.edge.flip_sign()
        self.assertEqual(self.edge.get_sign(), 0)
        # Flip the sign again to check if it toggles correctly
        self.edge.flip_sign()
        self.assertEqual(self.edge.get_sign(), 1)

    def test_set_fixed(self):
        # Test setting the edge as fixed
        self.edge.set_fixed()
        self.assertTrue(self.edge.get_fixed())

    def test_is_equal_without_check_sign(self):
        # Test the is_equal method without checking the sign
        edge_same = Edge(self.node_1, self.node_2, 0)
        # Should return True since start/end nodes are the same
        self.assertTrue(self.edge.is_equal(edge_same, False))

    def test_is_equal_with_check_sign(self):
        # Test the is_equal method with checking the sign
        edge_same_sign = Edge(self.node_1, self.node_2, 1)
        edge_different_sign = Edge(self.node_1, self.node_2, 0)
        # Should return True since start/end nodes and sign are the same
        self.assertTrue(self.edge.is_equal(edge_same_sign, True))
        # Use edge with different sign  and check again
        self.assertFalse(self.edge.is_equal(edge_different_sign, True))

    def test_is_equal_different_nodes(self):
        # Test the is_equal method with different start or end nodes
        node_3 = Node('node_3')
        edge_different_start = Edge(node_3, self.node_2, 1)
        edge_different_end = Edge(self.node_1, node_3, 1)
        # Should return False since start nodes are different
        self.assertFalse(self.edge.is_equal(edge_different_start, False))
        # Should return False since end nodes are different
        self.assertFalse(self.edge.is_equal(edge_different_end, False))

if __name__ == '__main__':
    unittest.main()