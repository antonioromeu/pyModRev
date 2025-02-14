"""
This module contains the AsyncUpdater class, which extends the \
    TimeSeriesUpdater
to provide asynchronous updating functionality with additional consistency \
    rules.
"""

import clingo
from updaters.time_series_updater import TimeSeriesUpdater


class AsyncUpdater(TimeSeriesUpdater):
    """
    This class extends TimeSeriesUpdater and introduces additional rules
    for handling consistency in asynchronous updates.
    """

    @staticmethod
    def add_specific_rules(ctl: clingo.Control, configuration) -> None:
        """
        This method loads configuration-specific rules into the control object\
              (ctl)
        and applies additional constraints based on the provided configuration.
        """
        # ctl.load(configuration['asp_cc_d_a'])
        ctl.add('base', [], '1{update(P,T,V):vertex(V)}1 :- exp(P), time(P,T), time(P,T+1).')
        ctl.add('base', [], 'vlabel(P,T+1,V,1) :- update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), not r_part(V), not topologicalerror(V), time(P,T+1).')
        ctl.add('base', [], 'vlabel(P,T+1,V,0) :- update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), not r_gen(V), not topologicalerror(V), time(P,T+1).')
        ctl.add('base', [], 'vlabel(P,T+1,V,S) :- not update(P,T,V), vlabel(P,T,V,S), time(P,T+1).')
        ctl.add('base', [], ':- update(P,T,V), vlabel(P,T,V,S), vlabel(P,T+1,V,S).')
        ctl.add('base', [], 'topologicalerror(V) :- time(P1,T1), time(P2,T2), T1 != T2, time(P1,T1+1), time(P2,T2+1), update(P1, T1, V), update(P2, T2, V), {vlabel(P1,T1,V1,S1) : vlabel(P2,T2,V1,S2), functionAnd(V,Id, V1), S1!=S2}0, vlabel(P1,T1+1,V,S3), vlabel(P2,T2+1,V,S4), S3 != S4, not input(V).')
        ctl.add('base', [], 'topologicalerror(V) :- time(P1,T), time(P2,T), time(P1,T+1), time(P2,T+1), update(P1, T, V), update(P2, T, V), P1 != P2, {vlabel(P1,T,V1,S1) : vlabel(P2,T,V1,S2), S1!=S2,  functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
        ctl.add('base', [], 'repair(V) :- topologicalerror(V).')
        ctl.add('base', [], '#minimize {1@2,top,V : topologicalerror(V)}.')
        ctl.add('base', [], '#show update/3.')
        ctl.add('base', [], '#show topologicalerror/1.')
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V),\
                     1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), \
                    exp(P), r_part(V), not topologicalerror(V), time(P,T+1).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V),\
                     {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), \
                    exp(P), functionOr(V,_), r_gen(V), not topologicalerror(V)\
                    , time(P,T+1).')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T1), time(P2,T2), \
                    T1 != T2, time(P1,T1+1), time(P2,T2+1), update(P1, T1, V),\
                    update(P2, T2, V), {vlabel(P1,T1,V1,S1) : vlabel(P2,T2,V1,\
                    S2), functionAnd(V,Id, V1), S1!=S2}0, vlabel(P1,T1+1,V,S3)\
                    , vlabel(P2,T2+1,V,S4), S3 != S4, not input(V), P1 <= P2.')
            ctl.add('base', [], 'incT(P1,P2,V) :- time(P1,T), time(P2,T), \
                    time(P1,T+1), time(P2,T+1), update(P1, T, V), update(P2, \
                    T, V), P1 < P2, {vlabel(P1,T,V1,S1) : vlabel(P2,T,V1,S2), \
                    S1!=S2, functionAnd(V,Id, V1)}0, vlabel(P1,T+1,V,S3), \
                    vlabel(P2,T+1,V,S4), S3 != S4, not input(V).')
            ctl.add('base', [], '#show incT/3.')
