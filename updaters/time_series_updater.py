from abc import abstractmethod
from updaters.updater import Updater
from configuration import UpdateType

class TimeSeriesUpdater(Updater):
    @abstractmethod
    def add_specific_rules(ctl, configuration):
        pass
    
    @staticmethod
    def apply_update_rules(ctl, update_type, configuration):
        ctl.load(configuration['asp_cc_d'])
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), input(V), vlabel(P,T,V,0), exp(P), time(P,T+1), r_gen(V).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), input(V), vlabel(P,T,V,1), exp(P), time(P,T+1), r_part(V).')
            ctl.add('base', [], '#show inc/2.')
        if update_type == UpdateType.ASYNC.value:
            from updaters.async_updater import AsyncUpdater
            AsyncUpdater.add_specific_rules(ctl, configuration)
        elif update_type == UpdateType.SYNC.value:
            from updaters.sync_updater import SyncUpdater
            SyncUpdater.add_specific_rules(ctl, configuration)
        elif update_type == UpdateType.MASYNC.value:
            from updaters.multi_async_updater import MultiAsyncUpdater
            MultiAsyncUpdater.add_specific_rules(ctl, configuration)