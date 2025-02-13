"""
This module contains the TimeSeriesUpdater class, which provides an abstract \
    base
class for managing time series updates. The class enforces the implementation
of specific update rules and applies these rules based on the configuration.
"""

from abc import abstractmethod
import clingo
from updaters.updater import Updater


class TimeSeriesUpdater(Updater):
    """
    This class extends the Updater class and defines the basic structure for \
        time
    series update rules. It is meant to be subclassed and extended by specific
    update types (e.g., asynchronous, synchronous, multi-asynchronous).
    """

    @staticmethod
    @abstractmethod
    def add_specific_rules(ctl: clingo.Control, configuration):
        """
        Subclasses must implement this method to define rules that are specific
        to the type of update (e.g., async, sync, or multi-async).
        """

    @staticmethod
    def apply_update_rules(ctl: clingo.Control, update_type: int,
                           configuration) -> None:
        """
        This method applies general update rules and calls the specific update
        rules depending on the update type (asynchronous, synchronous, or \
            multi-async).
        It loads the configuration and applies consistency checks as required.
        """
        ctl.load(configuration['asp_cc_d'])
        if configuration['check_consistency']:
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,1), input(V), \
                    vlabel(P,T,V,0), exp(P), time(P,T+1), r_gen(V).')
            ctl.add('base', [], 'inc(P,V) :- vlabel(P,T+1,V,0), input(V), \
                    vlabel(P,T,V,1), exp(P), time(P,T+1), r_part(V).')
            ctl.add('base', [], '#show inc/2.')
        updater_class = Updater.get_updater(update_type)
        updater_class.add_specific_rules(ctl, configuration)
