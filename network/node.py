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