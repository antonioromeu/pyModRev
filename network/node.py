from function import Function
import unittest

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

# class MyTestCase(unittest.TestCase):
#     def test_node_creation(self):
#         node = Node(1)
#         function = Function(1)
#         self.assertEqual(node.get_id(), 1)
#         self.assertEqual(node.get_function(), function)