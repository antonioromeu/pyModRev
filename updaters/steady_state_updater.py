"""
This module contains the SteadyStateUpdater class, which extends the Updater \
    class
to handle steady-state updates while ensuring consistency constraints.
"""

from updater import Updater


class SteadyStateUpdater(Updater):
    """
    This class extends Updater and applies specific rules to ensure
    consistent updates in a steady-state system.
    """

    @staticmethod
    def apply_update_rules(ctl, update_type, configuration):
        """
        This method loads configuration-defined rules into the control object \
            (ctl)
        and applies consistency constraints based on the provided \
            configuration.
        """
        ctl.load(configuration['asp_cc_ss'])
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,0), 1{noneNegative(P,V\
                    ,Id):functionOr(V,Id)}, vertex(V), ss(P), r_part(V).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,1), {noneNegative(P,V \
                    ,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_)\
                    , r_gen(V).')
            ctl.add('base', [], '#show inc/2.')
