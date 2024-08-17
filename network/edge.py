import unittest
from network.node import Node

class Edge:
    def __init__(self, start_node: Node, end_node: Node, sign: int) -> None:
        self.start_node = start_node
        self.end_node = end_node
        self.sign = sign
        self.fixed = False

    def get_start_node(self) -> Node:
        return self.start_node

    def get_end_node(self) -> Node:
        return self.end_node

    def get_sign(self) -> int:
        return self.sign
    
    def get_fixed(self) -> bool:
        return self.fixed

    def flip_sign(self) -> None:
        self.sign = 1 if self.sign == 0 else 0

    def set_fixed(self) -> None:
        self.fixed = True

    def is_equal(self, edge, check_sign: bool) -> bool:
        if self.start_node.get_id() != edge.get_start_node().get_id() or \
                self.end_node.get_id() != edge.get_end_node().get_id():
            return False
        if check_sign:
            return self.sign == edge.get_sign()
        return True

# class TestEdge(unittest.TestCase):
#     def setUp(self):
#         self.node1 = Node(1)
#         self.node2 = Node(2)
#         self.edge = Edge(self.node1, self.node2, 1)

#     def test_get_start_node(self):
#         self.assertEqual(self.edge.get_start_node(), self.node1)

#     def test_get_end_node(self):
#         self.assertEqual(self.edge.get_end_node(), self.node2)

#     def test_get_sign(self):
#         self.assertEqual(self.edge.get_sign(), 1)

#     def test_flip_sign(self):
#         self.edge.flip_sign()
#         self.assertEqual(self.edge.get_sign(), 0)
#         self.edge.flip_sign()
#         self.assertEqual(self.edge.get_sign(), 1)

#     def test_is_fixed(self):
#         self.assertFalse(self.edge.is_fixed())

#     def test_set_fixed(self):
#         self.edge.set_fixed()
#         self.assertTrue(self.edge.is_fixed())

#     def test_is_equal_without_check_sign(self):
#         edge_same = Edge(self.node1, self.node2, 0)
#         self.assertTrue(self.edge.is_equal(edge_same, False))

#     def test_is_equal_with_check_sign(self):
#         edge_same_sign = Edge(self.node1, self.node2, 1)
#         edge_different_sign = Edge(self.node1, self.node2, 0)
#         self.assertTrue(self.edge.is_equal(edge_same_sign, True))
#         self.assertFalse(self.edge.is_equal(edge_different_sign, True))

#     def test_is_equal_different_nodes(self):
#         node3 = Node(3)
#         edge_different_start = Edge(node3, self.node2, 1)
#         edge_different_end = Edge(self.node1, node3, 1)
#         self.assertFalse(self.edge.is_equal(edge_different_start, False))
#         self.assertFalse(self.edge.is_equal(edge_different_end, False))

# if __name__ == '__main__':
#     unittest.main()