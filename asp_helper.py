from enum import Enum
import clingo
import configuration
import util_h

class UpdateType(Enum):
    ASYNC = 0
    SYNC = 1
    MASYNC = 2

class ASPHelper:
    @staticmethod
    def check_consistency(network, optimization, update):
        result = []

        try:
            def logger(warning_code, message):
                if configuration.is_active("debug"):
                    print(message)

            ctl = clingo.Control(arguments=["--opt-mode=optN"], logger=logger, message_limit=20)

            ctl.load(configuration.get_value("ASP_CC_BASE"))

            if network.has_ss_obs:
                ctl.load(configuration.get_value("ASP_CC_SS"))
                if configuration.is_active("checkConsistency"):
                    ctl.add("base", [], "inc(P,V) :- vlabel(P,V,0), 1{noneNegative(P,V,Id):functionOr(V,Id)}, vertex(V), ss(P), r_part(V).")
                    ctl.add("base", [], "inc(P,V) :- vlabel(P,V,1), {noneNegative(P,V,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_), r_gen(V).")
                    ctl.add("base", [], "#show inc/2.")

            if network.has_ts_obs:
                ctl.load(configuration.get_value("ASP_CC_D"))
                if configuration.is_active("checkConsistency"):
                    ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,1), input(V), vlabel(P,T,V,0), exp(P), time(P,T+1), r_gen(V).")
                    ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,0), input(V), vlabel(P,T,V,1), exp(P), time(P,T+1), r_part(V).")
                    ctl.add("base", [], "#show inc/2.")

                if update == UpdateType.ASYNC:
                    ctl.load(configuration.get_value("ASP_CC_D_A"))
                    if configuration.is_active("checkConsistency"):
                        ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), not topologicalerror(V), time(P,T+1).")
                        ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V), time(P,T+1).")
                        ctl.add("base", [], "incT(P1,P2,V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), update(P1, T1, V), update(P2, T2, V), {vlabel(P1,T1,V1,S1) : vlabel(P2,T2,V1,S2), functionAnd(V,Id, V1), S1!=S2}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.")
                        ctl.add("base", [], "incT(P1,P2,V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), update(P1, T, V), update(P2, T, V), P1 < P2, {vlabel(P1,T,V1,S1) : vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).")
                        ctl.add("base", [], "#show incT/3.")

                elif update == UpdateType.SYNC:
                    ctl.load(configuration.get_value("ASP_CC_D_S"))
                    if configuration.is_active("checkConsistency"):
                        ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,0), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), not topologicalerror(V), time(P,T), time(P,T+1).")
                        ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,1), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V), time(P,T), time(P,T+1).")
                        ctl.add("base", [], "incT(P1,P2,V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), vertex(V), {vlabel(P1,T1,V1,S1): vlabel(P2,T2,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.")
                        ctl.add("base", [], "incT(P1,P2,V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), exp(P1), exp(P2), P1 < P2, vertex(V), {vlabel(P1,T,V1,S1): vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).")
                        ctl.add("base", [], "#show incT/3.")

                elif update == UpdateType.MASYNC:
                    ctl.load(configuration.get_value("ASP_CC_D_MA"))
                    if configuration.is_active("checkConsistency"):
                        ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), time(P,T)+1.")
                        ctl.add("base", [], "inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), time(P,T+1).")

            ctl.load(network.input_file_network)
            for obs_file in network.observation_files:
                ctl.load(obs_file)

            ctl.ground([("base", [])])
            with ctl.solve(yield_=True) as handle:
                for model in handle:
                    if model.optimality_proven:
                        result.append(ASPHelper.parse_cc_model(model, optimization))

            if not result:
                optimization = -1

        except Exception as e:
            print(f"failed to check consistency: {e}")

        return result

    @staticmethod
    def parse_cc_model(model, optimization):
        inconsistency = InconsistencySolution()
        count = 0
        for atom in model.symbols(shown=True):
            name = atom.name
            args = atom.arguments

            if name == "vlabel":
                if len(args) > 3:
                    inconsistency.add_vlabel(str(args[0]), str(args[2]), args[3].number, args[1].number)
                else:
                    inconsistency.add_vlabel(str(args[0]), str(args[1]), args[2].number, 0)
                continue
            if name == "r_gen":
                inconsistency.add_generalization(str(args[0]))
                continue
            if name == "r_part":
                inconsistency.add_particularization(str(args[0]))
                continue
            if name == "repair":
                count += 1
                continue
            if name == "update":
                inconsistency.add_update(args[1].number, str(args[0]), str(args[2]))
                continue
            if name == "topologicalerror":
                inconsistency.add_topological_error(str(args[0]))
                continue
            if name == "inc":
                inconsistency.add_inconsistent_profile(str(args[0]), str(args[1]))
                continue
            if name == "incT":
                inconsistency.add_inconsistent_profile(str(args[0]), str(args[2]))
                inconsistency.add_inconsistent_profile(str(args[1]), str(args[2]))
                continue

        optimization = count
        return inconsistency

    @staticmethod
    def parse_network(network):
        result = 1

        try:
            with open(network.input_file_network, 'r') as file:
                for count_line, line in enumerate(file, start=1):
                    line = line.replace(" ", "").strip()
                    if ")." in line:
                        predicates = line.split(").")
                        for i in range(len(predicates) - 1):
                            predicates[i] += ")."
                            if "vlabel" in predicates[i]:
                                result = util_h.parse_clingo_vlabel(predicates[i], network, count_line)
                                if result != 0:
                                    break
                    else:
                        if "vlabel" in line:
                            result = util_h.parse_clingo_vlabel(line, network, count_line)
                            if result != 0:
                                break
        except Exception as e:
            print(f"failed to parse clingo network: {e}")

        return result