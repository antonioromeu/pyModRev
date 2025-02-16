"""
This module provides the ASPHelper class, which contains utility methods for
working with Answer Set Programming (ASP) in network analysis.
It includes methods for validating input names, parsing network files,
checking consistency, and parsing ASP models to extract inconsistencies.
"""

from typing import List, Tuple
import clingo
from network.network import Network
from network.inconsistency_solution import Inconsistency_Solution
from configuration import configuration
from updaters.updater import Updater


class ASPHelper:
    """
    A utility class for handling ASP-related tasks in network analysis.
    Provides methods for validating input names, parsing network files,
    checking consistency, and parsing ASP models.
    """

    @staticmethod
    def validate_input_name(s: str) -> bool:
        """
        Checks if the input name follows the required naming conventions.
        """
        if s[0] != '"' and not s[0].islower() and not s[0].isdigit():
            return False
        return True

    @staticmethod
    def parse_network(network: Network) -> int:
        """
        Parses a network file and populates the provided Network object with
        nodes, edges, and other properties.
        """
        result = 1
        try:
            with open(network.get_input_file_network(), 'r', encoding="utf-8")\
                 as file:
                count_line = 0
                for line in file:
                    count_line += 1
                    line = ''.join(line.split())  # Remove all whitespace
                    if ').' in line:
                        predicates = line.split(')')
                        for i in range(len(predicates) - 1):
                            predicates[i] += ').'
                            if i > 0:
                                predicates[i] = predicates[i][1:]
                            split = predicates[i].split('(')

                            if split[0] == 'vertex':
                                node = split[1].split(')')[0]
                                network.add_node(node)
                                continue

                            elif split[0] == 'edge':
                                split = split[1].split(')')
                                split = split[0].split(',')

                                if len(split) != 3:
                                    print(f'WARN!\tEdge not recognized in line\
                                           {str(count_line)}: {predicates[i]}')
                                    result = -1
                                    continue

                                if not ASPHelper.validate_input_name(split[0]) or not ASPHelper.validate_input_name(split[1]):
                                    print(f'WARN!\tInvalid node argument in line {str(count_line)}: {predicates[i]}')
                                    print('\t\tNodes names must start with a lower case letter, a digit, or be surrounded by quotation marks.')
                                    return -2

                                start_id, end_id = split[0], split[1]
                                try:
                                    sign = int(split[2])
                                except ValueError:
                                    print(f'WARN!\tInvalid edge sign: {split[2]} on line {str(count_line)} in edge {predicates[i]}')
                                    return -2

                                if sign not in [0, 1]:
                                    print(f'WARN!\tInvalid edge sign on line {str(count_line)} in edge {predicates[i]}')
                                    return -2

                                start_node = network.add_node(start_id)
                                end_node = network.add_node(end_id)
                                network.add_edge(start_node, end_node, sign)
                                continue

                            elif split[0] == 'fixed':

                                split = split[1].split(')')
                                split = split[0].split(',')

                                if len(split) != 2:
                                    continue

                                if not ASPHelper.validate_input_name(split[0]) or not ASPHelper.validate_input_name(split[1]):
                                    print(f'WARN!\tInvalid node argument in line {count_line}: {predicates[i]}')
                                    print('\t\tNodes names must start with a lower case letter, a digit, or be surrounded by quotation marks.')
                                    return -2

                                start_id, end_id = split[0], split[1]
                                edge = network.get_edge(start_id, end_id)

                                if edge is not None:
                                    edge.set_fixed()
                                else:
                                    print(f'WARN!\tUnrecognized edge on line {count_line}: {predicates[i]} Ignoring...')
                                continue

                            elif split[0] == 'functionOr':
                                split = split[1].split(')')
                                split = split[0].split(',')

                                if len(split) != 2:
                                    print(f'WARN!\tfunctionOr not recognized on line {str(count_line)}: {predicates[i]}')
                                    result = -1
                                    continue

                                if not ASPHelper.validate_input_name(split[0]):
                                    print(f'WARN!\tInvalid node argument in line {str(count_line)}: {predicates[i]}')
                                    print('\t\tNodes names must start with a lower case letter, a digit, or be surrounded by quotation marks.')
                                    return -2

                                network.add_node(split[0])

                                if '..' in split[1]:
                                    split = split[1].split('.')
                                    try:
                                        range_limit = int(split[-1])
                                    except ValueError:
                                        print(f'WARN!\tInvalid range limit: {split[-1]} on line {count_line} in {predicates[i]}. It must be an integer greater than 0.')
                                        return -2
                                    if range_limit < 1:
                                        print(f'WARN!\tInvalid range limit: {range_limit} on line {count_line} in {predicates[i]}. It must be an integer greater than 0.')
                                        return -2

                                else:
                                    try:
                                        range_limit = int(split[1])
                                        if range_limit < 1:
                                            print(f'WARN!\tInvalid range limit: {range_limit} on line {count_line} in {predicates[i]}. It must be an integer greater than 0.')
                                            return -2
                                    except ValueError:
                                        print(f'WARN!\tInvalid functionOr range definition on line {count_line}: {predicates[i]}')
                                        return -2
                                continue

                            elif split[0] == 'functionAnd':
                                split = split[1].split(')')
                                split = split[0].split(',')

                                if len(split) != 3:
                                    print(f'WARN!\tfunctionAnd not recognized on line {count_line}: {predicates[i]}')
                                    result = -1
                                    continue

                                if not ASPHelper.validate_input_name(split[0]) or not ASPHelper.validate_input_name(split[2]):
                                    print(f'WARN!\tInvalid node argument on line {count_line}: {predicates[i]}')
                                    print('\t\tNodes names must start with a lower case letter, a digit, or be surrounded by quotation marks.')
                                    return -2

                                node = network.get_node(split[0])
                                if node is None:
                                    print(f'WARN!\tNode not recognized or not yet defined: {split[0]} on line {count_line} in {predicates[i]}')
                                    result = -1
                                    continue

                                node2 = network.get_node(split[2])
                                if node2 is None:
                                    print(f'WARN!\tNode not recognized or not yet defined: {split[2]} on line {count_line} in {predicates[i]}')
                                    result = -1
                                    continue

                                try:
                                    clause_id = int(split[1])
                                    if clause_id < 1:
                                        print(f'WARN!\tInvalid clause Id: {split[1]} on line {count_line} in {predicates[i]}')
                                        result = -1
                                        continue
                                except ValueError:
                                    print(f'WARN!\tInvalid clause Id: {split[1]} on line {count_line} in {predicates[i]}')
                                    result = -1
                                    continue
                                node.get_function().add_regulator_to_term(clause_id, split[2])
                                continue
        except IOError as exc:
            raise ValueError('ERROR!\tCannot open file ' +
                             network.get_input_file_network()) from exc
        return result

    @staticmethod
    def check_consistency(network: Network, update_type: int) -> Tuple[List[
            Inconsistency_Solution], int]:
        """
        Checks the consistency of the network based on the specified update
        type.
        """
        result = []
        optimization = -2
        updater = Updater.get_updater(update_type)
        result, optimization = updater.check_consistency(network, update_type,
                                                         configuration)
        return result, optimization

    @staticmethod
    def parse_cc_model(model: clingo.Model) -> Tuple[Inconsistency_Solution,
                                                     int]:
        """
        Parses a clingo model to extract inconsistency information.
        """
        inconsistency = Inconsistency_Solution()
        count = 0
        for atom in model.symbols(atoms=True):
            name = atom.name
            args = atom.arguments
            if name == 'vlabel':
                if len(args) > 3:
                    inconsistency.add_v_label(str(args[0]), str(args[2]),
                                              int(str(args[3])),
                                              int(str(args[1])))
                else:
                    inconsistency.add_v_label(str(args[0]), str(args[1]),
                                              int(str(args[2])), 0)
                continue
            if name == 'r_gen':
                inconsistency.add_generalization(str(args[0]))
                continue
            if name == 'r_part':
                inconsistency.add_particularization(str(args[0]))
                # FIXME why doesn't it have continue like other IFs
                # continue
            if name == 'repair':
                count += 1
                continue
            if name == 'update':
                inconsistency.add_update(int(str(args[1])), str(args[0]),
                                         str(args[2]))
                continue
            if name == 'topologicalerror':
                inconsistency.add_topological_error(str(args[0]))
                continue
            if name == 'inc':
                inconsistency.add_inconsistent_profile(str(args[0]),
                                                       str(args[1]))
                continue
            if name == 'incT':
                inconsistency.add_inconsistent_profile(str(args[0]),
                                                       str(args[2]))
                inconsistency.add_inconsistent_profile(str(args[1]),
                                                       str(args[2]))
                continue
        return inconsistency, count
