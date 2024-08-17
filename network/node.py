import unittest
from network.function import Function

class Node:
    def __init__(self, id: str) -> None:
        self.id = id
        self.function = Function(id)

    def add_function(self, function: Function) -> None:
        self.function = function

    def get_function(self) -> Function:
        return self.function

    def get_id(self) -> str:
        return self.id

# class TestNode(unittest.TestCase):
#     def setUp(self):
#         self.node = Node(1)
#         self.function = Function(2)

#     def test_initialization(self):
#         self.assertEqual(self.node.get_id(), 1)
#         self.assertEqual(self.node.get_function().get_id(), 1)

#     def test_add_function(self):
#         self.node.add_function(self.function)
#         self.assertEqual(self.node.get_function().get_id(), 2)

#     def test_get_function(self):
#         self.assertEqual(self.node.get_function().get_id(), 1)
#         self.node.add_function(self.function)
#         self.assertEqual(self.node.get_function().get_id(), 2)

#     def test_get_id(self):
#         self.assertEqual(self.node.get_id(), 1)

# if __name__ == '__main__':
#     unittest.main()