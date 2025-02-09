from updaters.time_series_updater import TimeSeriesUpdater

class MultiAsyncUpdater(TimeSeriesUpdater):
    @staticmethod
    def add_specific_rules(ctl, configuration):
        ctl.load(configuration['asp_cc_d_ma'])
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), update(P,T,V), 1{noneNegative(P,T,V,Id):functionOr(V,Id)}, vertex(V), exp(P), r_part(V), time(P,T)+1.')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), update(P,T,V), {noneNegative(P,T,V,Id):functionOr(V,Id)}0, vertex(V), exp(P), functionOr(V,_), r_gen(V), time(P,T+1).')