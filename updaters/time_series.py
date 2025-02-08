from abc import abstractmethod
from updater import Updater

class TimeSeriesUpdater(Updater):
    def __init__(self):
        super().__init__("time_series")
    
    @abstractmethod
    def add_specific_rules(self, ctl, configuration):
        pass

    def apply_update_rules(self, ctl, network, configuration):
        if network.get_has_ts_obs():
            ctl.load(configuration['asp_cc_d'])
            if configuration['check_consistency']:
                ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), input(V), vlabel(P,T,V,0), exp(P), time(P,T+1), r_gen(V).')
                ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), input(V), vlabel(P,T,V,1), exp(P), time(P,T+1), r_part(V).')
                ctl.add('base', [], '#show inc/2.')
            self.add_specific_rules(ctl, configuration)