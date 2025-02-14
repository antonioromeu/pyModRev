"""
This module contains the MultiAsyncUpdater class, which extends \
    TimeSeriesUpdater
to handle multiple asynchronous updates while ensuring consistency.
"""

import clingo
from updaters.time_series_updater import TimeSeriesUpdater


class CompleteUpdater(TimeSeriesUpdater):
    """
    This class extends TimeSeriesUpdater and applies additional rules
    to handle multiple asynchronous updates while enforcing consistency checks.
    """
    @staticmethod
    def add_specific_rules(ctl: clingo.Control, configuration) -> None:
        """
        This method loads a configuration-defined rule set into the control \
            object (ctl)
        and applies consistency constraints if enabled.
        """
        # ctl.load(configuration['asp_cc_d_ma'])
        ctl.add('base', [], '1{update(P,T,V):vertex(V)} :- exp(P), time(P,T), \
                time(P,T+1).')
        ctl.add('base', [], 'vlabel(P,T+1,V,1) :- update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), not r_part(V), time(P,T+1).')
        ctl.add('base', [], 'vlabel(P,T+1,V,0) :- update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), not r_gen(V), time(P,T+1).')
        ctl.add('base', [], 'vlabel(P,T+1,V,S) :- not update(P,T,V), vlabel(P,T,V,S), time(P,T+1).')
        ctl.add('base', [], '#show update/3.')
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V),\
                     1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), \
                    exp(P), r_part(V), time(P,T+1).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V),\
                     {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), \
                    exp(P), functionOr(V,_), r_gen(V), time(P,T+1).')
