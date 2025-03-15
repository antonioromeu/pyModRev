"""
This module defines the Network class, which represents a network of nodes and
edges.
The Network class provides methods to manage nodes, edges, and network-related
properties such as input files and observations.
"""

from typing import Dict, List
from network.node import Node
from network.edge import Edge


class Network:
    """
    Represents a network of nodes and edges.
    Provides methods to manage nodes, edges, and network-related properties
    such as input files and observations.
    """
    def __init__(self) -> None:
        """
        Initializes an empty network with no nodes, edges, or input files.
        """
        self.nodes = {}  # {'node_id_1': node_1, 'node_id_2': node_2, ...}
        # self.edges = []
        # self.graph = {} # {'node_id_1': ['node_id_2', 'node_id_3'], 'node_id_2': ['node_id_1'], ...}
        self.graph = {}  # {'node_id_1': [edge_1_2, edge_1_3], 'node_id_2': [edge_2_1], ...}
        self.regulators = {}  # Reverse of graph {'node_id_1': ['node_id_2'], 'node_id_2': ['node_id_1'], 'node_id_3': ['node_id_1'], ...}
        self.input_file_network = ''
        self.observation_files = []
        self.observation_files_with_updater = []  # [('examples/fissionYeastDavidich2008/obs/ts/ssync/s_o1_t5.lp', <sync_updater.SyncUpdater object at 0x10c7bea90>)]
        self.has_ss_obs = False
        self.has_ts_obs = False

    def get_node(self, node_id: str) -> Node:
        """
        Retrieves a node from the network by its identifier.
        """
        node = None
        if node_id in self.nodes:
            node = self.nodes[node_id]
        return node

    def get_nodes(self) -> Dict[str, Node]:
        """
        Returns all nodes in the network as a dictionary.
        """
        return self.nodes

    def get_edge(self, start_node_id: str, end_node_id: str) -> Edge:
        """
        Retrieves an edge between two nodes by their identifiers.
        """
        # for edge in self.edges:
        #     if edge.get_start_node().get_id() == start_node_id \
        #             and edge.get_end_node().get_id() == end_node_id:
        #         return edge
        for edge in self.graph[start_node_id]:
            if edge.get_end_node().get_id() == end_node_id:
                return edge
        raise ValueError('Edge does not exist!')

    def get_graph(self) -> Dict[str, List[Edge]]:
        """
        Returns the graph representation of the network.
        """
        return self.graph

    def get_regulators(self) -> Dict[str, List[str]]:
        """
        Returns the regulators of each node in the network.
        """
        return self.regulators

    # def get_edges(self) -> List[Edge]:
    #     return self.edges

    def get_input_file_network(self) -> str:
        """
        Returns the input file associated with the network.
        """
        return self.input_file_network

    def get_observation_files(self) -> List:
        """
        Returns the list of observation files associated with the network.
        """
        return self.observation_files

    def get_observation_files_with_updater(self) -> List:
        """
        Returns the list of observation files associated with the network.
        """
        return self.observation_files_with_updater

    def get_has_ss_obs(self) -> bool:
        """
        Returns whether the network has steady-state observations.
        """
        return self.has_ss_obs

    def get_has_ts_obs(self) -> bool:
        """
        Returns whether the network has time-series observations.
        """
        return self.has_ts_obs

    def add_node(self, node_id: str) -> Node:
        """
        Adds a new node to the network with the given identifier.
        """
        node = self.get_node(node_id)
        if node is None:
            node = Node(node_id)
            self.nodes[node_id] = node
            self.graph[node_id] = []
        return node

    def add_edge(self, start_node: Node, end_node: Node, sign: int) -> None:
        """
        Adds a new edge between two nodes with the specified sign.
        """
        try:
            return self.get_edge(start_node.get_id(), end_node.get_id())
        except ValueError:
            edge = Edge(start_node, end_node, sign)
            # self.edges.append(edge)
            self.graph[edge.get_start_node().get_id()].append(edge)
            if edge.get_end_node().get_id() not in self.regulators:
                self.regulators[edge.get_end_node().get_id()] = \
                    [edge.get_start_node().get_id()]
            else:
                self.regulators[edge.get_end_node().get_id()].append(
                    edge.get_start_node().get_id())
            # return edge

    def remove_edge(self, start_node: Node, end_node: Node) -> None:
        """
        Removes an edge between two nodes from the network.
        """
        try:
            edge_to_remove = self.get_edge(start_node.get_id(),
                                           end_node.get_id())  # Find the edge to remove
            self.graph[start_node.get_id()].remove(edge_to_remove)  # Remove the edge from the graph
            self.regulators[end_node.get_id()].remove(start_node.get_id())  # Remove the start_node from the list of regulators for the end_node
            if not self.regulators[end_node.get_id()]:  # If there are no more regulators for the end_node, remove the key from the regulators dictionary
                del self.regulators[end_node.get_id()]
        except ValueError:
            print(f"No edge exists between {start_node.get_id()} and {end_node.get_id()}")

    def set_has_ss_obs(self, has_ss_obs: bool) -> None:
        """
        Sets whether the network has steady-state observations.
        """
        self.has_ss_obs = has_ss_obs

    def set_has_ts_obs(self, has_ts_obs: bool) -> None:
        """
        Sets whether the network has time-series observations.
        """
        self.has_ts_obs = has_ts_obs

    def set_input_file_network(self, input_file_netowrk: str) -> None:
        """
        Sets the input file associated with the network.
        """
        self.input_file_network = input_file_netowrk

    def add_observation_file(self, observation_file: str) -> None:
        """
        Adds an observation file to the network.
        """
        self.observation_files.append(observation_file)

    def add_observation_file_with_updater(self, observation_file: str, updater) -> None:
        """
        Adds an observation file and respective updater to the network.
        """
        self.observation_files_with_updater.append((observation_file, updater))
