from time_series import TimeSeriesUpdater

class SyncUpdater(TimeSeriesUpdater):
    def __init__(self):
        super().__init__("sync")

    def apply_update_rules(self, ctl, network, configuration):
        ctl.load(configuration['asp_cc_d_s'])
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), not topologicalerror(V), time(P,T), time(P,T+1).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V), time(P,T), time(P,T+1).')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), vertex(V), {vlabel(P1,T1,V1,S1): vlabel(P2,T2,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), exp(P1), exp(P2), P1 < P2, vertex(V), {vlabel(P1,T,V1,S1): vlabel(P2,T,V1,S2), S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
            ctl.add('base', [], '#show incT/3.')