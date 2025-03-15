"""
This module contains the TimeSeriesUpdater class, which provides an abstract
base class for managing time series updates. The class enforces the
implementation of specific update rules and applies these rules based on the
configuration.
"""

from abc import abstractmethod
import clingo
from updaters.updater import Updater
from configuration import configuration


class TimeSeriesUpdater(Updater):
    """
    This class extends the Updater class and defines the basic structure for
    time series update rules. It is meant to be subclassed and extended by
    specific update types (e.g., asynchronous, synchronous, complete)
    """

    @staticmethod
    @abstractmethod
    def add_specific_rules(ctl: clingo.Control):
        """
        Subclasses must implement this method to define rules that are specific
        to the type of update (e.g., async, sync, or complete).
        """

    @staticmethod
    def apply_update_rules(ctl: clingo.Control, updater) -> None:
        """
        This method applies general update rules and calls the specific update
        rules depending on the update type (asynchronous, synchronous, or
        complete). It loads the configuration and applies consistency checks as
        required.
        """
        ctl.add('base', [], 'time(P,T) :- exp(P), obs_vlabel(P,T,_,_).')
        ctl.add('base', [], 'time(P,T) :- time(P,T+1), T+1 > 0.')
        ctl.add('base', [], '1{vlabel(P,T,V,S):sign(S)}1:-vertex(V), exp(P), time(P,T).')
        ctl.add('base', [], ':-vlabel(P,T,V,S1), obs_vlabel(P,T,V,S2), complement(S1,S2).')
        ctl.add('base', [], 'onePositive(P,T,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S), vlabel(P,T,V2,S), exp(P), time(P,T).')
        ctl.add('base', [], 'oneNegative(P,T,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S1), vlabel(P,T,V2,S2), complement(S1,S2), exp(P), time(P,T).')
        ctl.add('base', [], 'noneNegative(P,T,V,Id) :- onePositive(P,T,V,Id), not oneNegative(P,T,V,Id).')
        ctl.add('base', [], 'input(V) :- not functionOr(V,_), vertex(V).')
        ctl.add('base', [], 'vlabel(P,T+1,V,0) :- input(V), vlabel(P,T,V,0), exp(P), time(P,T+1), not r_gen(V).')
        ctl.add('base', [], 'vlabel(P,T+1,V,1) :- input(V), vlabel(P,T,V,1), exp(P), time(P,T+1), not r_part(V).')
        ctl.add('base', [], '#minimize {1@1,V : repair(V)}.')
        ctl.add('base', [], '#minimize {1@1,g,V : r_gen(V)}.')
        ctl.add('base', [], '#minimize {1@1,p,V : r_part(V)}.')
        ctl.add('base', [], '#show vlabel/4.')
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), input(V), \
                    vlabel(P,T,V,0), exp(P), time(P,T+1), r_gen(V).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), input(V), \
                    vlabel(P,T,V,1), exp(P), time(P,T+1), r_part(V).')
            ctl.add('base', [], '#show inc/2.')
        updater.add_specific_rules(ctl)

    @staticmethod
    def should_update(time: int, labeling, profile: str, function) -> bool:
        """
        Determines if the function should be considered for an update at the
        given time. In a time series scenario, this method checks if the
        function's node ID is in the updates list.
        """
        updates = labeling.get_updates()[time][profile]
        return any(update == function.get_node_id() for update in updates)

    # @staticmethod
    # def apply_update_rules(ctl: clingo.Control, update_type: int,) -> None:
    #     """
    #     This method applies general update rules and calls the specific update
    #     rules depending on the update type (asynchronous, synchronous, or
    #     complete). It loads the configuration and applies consistency checks as
    #     required.
    #     """
    #     # ctl.load(configuration['asp_cc_d'])
    #     ctl.add('base', [], 'time(P,T) :- exp(P), obs_vlabel(P,T,_,_).')
    #     ctl.add('base', [], 'time(P,T) :- time(P,T+1), T+1 > 0.')
    #     ctl.add('base', [], '1{vlabel(P,T,V,S):sign(S)}1:-vertex(V), exp(P), time(P,T).')
    #     ctl.add('base', [], ':-vlabel(P,T,V,S1), obs_vlabel(P,T,V,S2), complement(S1,S2).')
    #     ctl.add('base', [], 'onePositive(P,T,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S), vlabel(P,T,V2,S), exp(P), time(P,T).')
    #     ctl.add('base', [], 'oneNegative(P,T,V,Id) :- functionAnd(V,Id, V2), edge(V2,V,S1), vlabel(P,T,V2,S2), complement(S1,S2), exp(P), time(P,T).')
    #     ctl.add('base', [], 'noneNegative(P,T,V,Id) :- onePositive(P,T,V,Id), not oneNegative(P,T,V,Id).')
    #     ctl.add('base', [], 'input(V) :- not functionOr(V,_), vertex(V).')
    #     ctl.add('base', [], 'vlabel(P,T+1,V,0) :- input(V), vlabel(P,T,V,0), exp(P), time(P,T+1), not r_gen(V).')
    #     ctl.add('base', [], 'vlabel(P,T+1,V,1) :- input(V), vlabel(P,T,V,1), exp(P), time(P,T+1), not r_part(V).')
    #     ctl.add('base', [], '#minimize {1@1,V : repair(V)}.')
    #     ctl.add('base', [], '#minimize {1@1,g,V : r_gen(V)}.')
    #     ctl.add('base', [], '#minimize {1@1,p,V : r_part(V)}.')
    #     ctl.add('base', [], '#show vlabel/4.')
    #     if configuration['check_consistency']:
    #         ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), input(V), \
    #                 vlabel(P,T,V,0), exp(P), time(P,T+1), r_gen(V).')
    #         ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), input(V), \
    #                 vlabel(P,T,V,1), exp(P), time(P,T+1), r_part(V).')
    #         ctl.add('base', [], '#show inc/2.')
    #     updater_class = Updater.get_updater(update_type)
    #     updater_class.add_specific_rules(ctl)

    # @abstractmethod
    # @staticmethod
    # def is_func_consistent_with_label_with_profile(network, labeling, function, profile) -> bool:
    #     """
    #     Evaluates whether the function's regulatory logic aligns with the
    #     expected dynamic behavior of the network. This implementation assumes a
    #     time series (i.e. multiple time points) and does not handle a
    #     steady-state scenario.
    #     """

    # @abstractmethod
    # @staticmethod
    # def is_func_consistent_with_label(network, labeling, function) -> int:
    #     """
    #     Checks if a function is consistent with a labeling across all profiles.
    #     """

    # @staticmethod
    # def is_clause_satisfiable(clause, network, time_map, function) -> bool:
    #     """
    #     Evaluates whether a clause is satisfiable given the network and current time mapping.
    #     """
    #     regulators = function.bitarray_to_regulators(clause)
    #     for var in regulators:
    #         edge = network.get_edge(var, function.get_node_id())
    #         if edge is not None:
    #             # The clause is unsatisfied if the edge sign contradicts the value in time_map.
    #             if (edge.get_sign() > 0) == (time_map[var] == 0):
    #                 return False
    #         else:
    #             print(f"WARN: Missing edge from {var} to {function.get_node_id()}")
    #             return False
    #     return True
