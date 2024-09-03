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