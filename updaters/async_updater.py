from updaters.time_series_updater import TimeSeriesUpdater

class AsyncUpdater(TimeSeriesUpdater):
    @staticmethod
    def add_specific_rules(ctl, configuration):
        ctl.load(configuration['asp_cc_d_a'])
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), not topologicalerror(V), time(P,T+1).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V), time(P,T+1).')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), update(P1, T1, V), update(P2, T2, V), {vlabel(P1,T1,V1,S1) : vlabel(P2,T2,V1,S2), functionAnd(V,Id, V1), S1!=S2}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), update(P1, T, V), update(P2, T, V), P1 < P2, {vlabel(P1,T,V1,S1) : vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
            ctl.add('base', [], '#show incT/3.')