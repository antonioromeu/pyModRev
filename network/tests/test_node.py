import unittest
from network.function import Function
from network.node import Node

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node = Node('test_node')
        self.function = Function('test_function')

    def test_initialization(self):
        # Test if the Node initializes correctly with an ID and a Function
        self.assertEqual(self.node.get_id(), 'test_node')
        self.assertIsInstance(self.node.get_function(), Function)
        self.assertEqual(self.node.get_function().get_node_id(), 'test_node')

    def test_add_function(self):
        # Test if the function is added correctly
        self.node.add_function(self.function)
        self.assertEqual(self.node.get_function().get_node_id(), 'test_function')

    def test_get_function(self):
        # Test if get_function returns the correct function
        self.assertEqual(self.node.get_function().get_node_id(), 'test_node')
        self.node.add_function(self.function)
        self.assertEqual(self.node.get_function().get_node_id(), 'test_function')

    def test_get_id(self):
        self.assertEqual(self.node.get_id(), 'test_node')

if __name__ == '__main__':
    unittest.main()