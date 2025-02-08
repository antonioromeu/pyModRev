from updater import Updater

class SteadyStateUpdater(Updater):
    def __init__(self):
        super().__init__("steady_state")

    def apply_update_rules(self, ctl, network, configuration):
        ctl.load(configuration['asp_cc_ss'])
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,0), 1{noneNegative(P,V,Id):functionOr(V,Id)}, vertex(V), ss(P), r_part(V).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,V,1), {noneNegative(P,V,Id):functionOr(V,Id)}0, vertex(V), ss(P), functionOr(V,_), r_gen(V).')
            ctl.add('base', [], '#show inc/2.')