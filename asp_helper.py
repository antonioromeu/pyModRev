import clingo
import sys
from network.network import Network
from network.inconsistency_solution import Inconsistency_Solution
from configuration import configuration
from utils import validate_input_name
from typing import List, Tuple

class ASPHelper:
    @staticmethod
    def parse_network(network: Network) -> int:
        result = 1
        try:
            with open(network.get_input_file_network(), 'r') as file:
                count_line = 0
                for line in file:
                    count_line += 1
                    line = ''.join(line.split()) # Remove all whitespace
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
                                    print(f'WARN!\tEdge not recognized in line {str(count_line)}: {predicates[i]}')
                                    result = -1
                                    continue
                                
                                if not validate_input_name(split[0]) or not validate_input_name(split[1]):
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

                                if not validate_input_name(split[0]) or not validate_input_name(split[1]):
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

                                if not validate_input_name(split[0]):
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

                                if not validate_input_name(split[0]) or not validate_input_name(split[2]):
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
        except IOError:
            raise ValueError('ERROR!\tCannot open file ' + network.get_input_file_network())
        return result

    @staticmethod
    def check_consistency(network: Network, update: int) -> Tuple[List[Inconsistency_Solution], int]:
        result = []
        optimization = -2
        try:
            def logger(warning_code, message):
                if configuration['debug']:
                    print(warning_code, file=sys.stderr)
                    print(message, file=sys.stderr)

            ctl = clingo.Control(['--opt-mode=optN'], logger, 20)
            ctl.load(configuration['asp_cc_base'])
            # TODO filer = pkg_resources.resource_string(__name__, "asp/file.pl").decode()
            if network.get_has_ss_obs():
                ctl.load(configuration['asp_cc_ss'])
                if configuration['check_consistency']:
                    ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,0), 1{noneNegative(P,V,Id):functionOr(V,Id)}, vertex(V), ss(P), r_part(V).')
                    ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,1), {noneNegative(P,V,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_), r_gen(V).')
                    ctl.add('base', [], '#show inc/2.')

            if network.get_has_ts_obs():
                ctl.load(configuration['asp_cc_d'])
                if configuration['check_consistency']:
                    ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), input(V), vlabel(P,T,V,0), exp(P), time(P,T+1), r_gen(V).')
                    ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), input(V), vlabel(P,T,V,1), exp(P), time(P,T+1), r_part(V).')
                    ctl.add('base', [], '#show inc/2.')
                
                if update == 'ASYNC':
                    ctl.load(configuration['asp_cc_d_a'])
                    if configuration['check_consistency']:
                        ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), not topologicalerror(V), time(P,T+1).')
                        ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V), time(P,T+1).')
                        ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), update(P1, T1, V), update(P2, T2, V), {vlabel(P1,T1,V1,S1) : vlabel(P2,T2,V1,S2), functionAnd(V,Id, V1), S1!=S2}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.')
                        ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), update(P1, T, V), update(P2, T, V), P1 < P2, {vlabel(P1,T,V1,S1) : vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
                        ctl.add('base', [], '#show incT/3.')
                
                elif update == 'SYNC':
                    ctl.load(configuration['asp_cc_d_s'])
                    if configuration['check_consistency']:
                        ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), not topologicalerror(V), time(P,T), time(P,T+1).')
                        ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V), time(P,T), time(P,T+1).')
                        ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), vertex(V), {vlabel(P1,T1,V1,S1): vlabel(P2,T2,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.')
                        ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), exp(P1), exp(P2), P1 < P2, vertex(V), {vlabel(P1,T,V1,S1): vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
                        ctl.add('base', [], '#show incT/3.')
                
                elif update == 'MASYNC':
                    ctl.load(configuration['asp_cc_d_ma'])
                    if configuration['check_consistency']:
                        ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), time(P,T)+1.')
                        ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), time(P,T+1).')

            ctl.load(network.get_input_file_network())
            for obs_file in network.get_observation_files():
                ctl.load(obs_file)

            ctl.ground([('base', [])])
            with ctl.solve(yield_=True) as handle:
                if handle.get().satisfiable:
                    for model in handle:
                        if model and model.optimality_proven:
                            res, opt = ASPHelper.parse_cc_model(model)
                            result.append(res)
                            optimization = opt
                else:
                    optimization = -1
        except Exception as e:
            print(f'Failed to check consistency: {e}')
        return result, optimization
    
    @staticmethod
    def parse_cc_model(model: clingo.Model) -> Tuple[Inconsistency_Solution, int]:
        inconsistency = Inconsistency_Solution()
        count = 0
        for atom in model.symbols(atoms=True):
            name = atom.name
            args = atom.arguments
            if name == 'vlabel':
                if len(args) > 3:
                    inconsistency.add_v_label(str(args[0]), str(args[2]), int(str(args[3])), int(str(args[1])))
                else:
                    inconsistency.add_v_label(str(args[0]), str(args[1]), int(str(args[2])), 0)
                continue

            if name == 'r_gen':
                inconsistency.add_generalization(str(args[0]))
                continue

            if name == 'r_part':
                inconsistency.add_particularization(str(args[0]))
                # continue # FIXME why doesn't it have continue like other IFs

            if name == 'repair':
                count += 1
                continue

            if name == 'update':
                inconsistency.add_update(int(str(args[1])), str(args[0]), str(args[2]))
                continue

            if name == 'topologicalerror':
                inconsistency.add_topological_error(str(args[0]))
                continue

            if name == 'inc':
                inconsistency.add_inconsistent_profile(str(args[0]), str(args[1]))
                continue

            if name == 'incT':
                inconsistency.add_inconsistent_profile(str(args[0]), str(args[2]))
                inconsistency.add_inconsistent_profile(str(args[1]), str(args[2]))
                continue
        return inconsistency, count