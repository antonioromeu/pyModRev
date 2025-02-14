"""
This module contains the SteadyStateUpdater class, which extends the Updater \
    class
to handle steady-state updates while ensuring consistency constraints.
"""

import clingo
from updaters.updater import Updater


class SteadyStateUpdater(Updater):
    """
    This class extends Updater and applies specific rules to ensure
    consistent updates in a steady-state system.
    """

    @staticmethod
    def apply_update_rules(ctl: clingo.Control, update_type: int,
                           configuration) -> None:
        """
        This method loads configuration-defined rules into the control object \
            (ctl)
        and applies consistency constraints based on the provided \
            configuration.
        """
        # ctl.load(configuration['asp_cc_ss'])
        ctl.add('base', [], 'ss(P) :- exp(P), not time(P,_).')
        ctl.add('base', [], '1{vlabel(P,V,S):sign(S)}1 :- vertex(V), ss(P).')
        ctl.add('base', [], ':-vlabel(P,V,S1), obs_vlabel(P,V,S2),complement(S1,S2).')
        ctl.add('base', [], 'onePositive(P,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S), vlabel(P,V2,S), ss(P).')
        ctl.add('base', [], 'oneNegative(P,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S), vlabel(P,V2,T), complement(S,T), ss(P).')
        ctl.add('base', [], 'noneNegative(P,V,Id) :- onePositive(P,V,Id), not oneNegative(P,V,Id).')
        ctl.add('base', [], 'vlabel(P,V,1) :- 1{noneNegative(P,V,Id):functionOr(V,Id)}, vertex(V), ss(P), not r_part(V).')
        ctl.add('base', [], 'vlabel(P,V,0) :- {noneNegative(P,V,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_), not r_gen(V).')
        ctl.add('base', [], '#minimize {1,V : repair(V)}.')
        ctl.add('base', [], '#minimize {1,g,V : r_gen(V)}.')
        ctl.add('base', [], '#minimize {1,p,V : r_part(V)}.')
        ctl.add('base', [], '#show vlabel/3.')
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,0), 1{noneNegative(P,V\
                    ,Id):functionOr(V,Id)}, vertex(V), ss(P), r_part(V).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,1), {noneNegative(P,V \
                    ,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_)\
                    , r_gen(V).')
            ctl.add('base', [], '#show inc/2.')
