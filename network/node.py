import unittest
from function import Function

class Node:
    def __init__(self, id):
        self.id = id
        self.reg_function = Function(id)

    def __del__(self):
        del self.reg_function

    def add_function(self, regulation):
        self.reg_function = regulation
        return regulation

    def get_function(self):
        return self.reg_function

    def get_id(self):
        return self.id

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node = Node(1)
        self.function = Function(2)

    def test_initialization(self):
        self.assertEqual(self.node.get_id(), 1)
        self.assertEqual(self.node.get_function().get_id(), 1)

    def test_add_function(self):
        self.node.add_function(self.function)
        self.assertEqual(self.node.get_function().get_id(), 2)

    def test_get_function(self):
        self.assertEqual(self.node.get_function().get_id(), 1)
        self.node.add_function(self.function)
        self.assertEqual(self.node.get_function().get_id(), 2)

    def test_get_id(self):
        self.assertEqual(self.node.get_id(), 1)

if __name__ == '__main__':
    unittest.main()