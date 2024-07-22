from node import Node

class Edge:
    def __init__(self, start_node, end_node, sign):
        self.start_node = start_node
        self.end_node = end_node
        self.sign = sign
        self.fixed = False

    def get_start_node(self):
        return self.start_node

    def get_end_node(self):
        return self.end_node

    def get_sign(self):
        return self.sign

    def flip_sign(self):
        self.sign = 1 if self.sign == 0 else 0

    def is_fixed(self):
        return self.fixed

    def set_fixed(self):
        self.fixed = True

    def is_equal(self, edge, check_sign):
        if (self.start_node.get_id() != edge.get_start_node().get_id()) or (self.end_node.get_id() != edge.get_end_node().get_id()):
            return False
        if check_sign:
            return self.sign == edge.get_sign()
        return True