"""
This module defines enumerations and configuration settings for handling 
inconsistencies and update types in a network analysis system.
"""

from enum import Enum


class Inconsistencies(Enum):
    """
    Enumeration representing different levels of inconsistencies in the system.

    Attributes:
        CONSISTENT (int): No inconsistency detected.
        SINGLE_INC_GEN (int): A general single inconsistency.
        SINGLE_INC_PART (int): A partial single inconsistency.
        DOUBLE_INC (int): A double inconsistency.
    """
    CONSISTENT = 0
    SINGLE_INC_GEN = 1
    SINGLE_INC_PART = 2
    DOUBLE_INC = 3


class UpdateType(Enum):
    """
    Enumeration representing the types of update strategies that can be used.

    Attributes:
        ASYNC (int): Asynchronous update strategy.
        SYNC (int): Synchronous update strategy.
        MASYNC (int): Mixed asynchronous update strategy.
    """
    ASYNC = 0
    SYNC = 1
    MASYNC = 2


configuration = {
    'verbose': 2,
    'version': '1.0.0',
    'update': UpdateType.ASYNC,  # Setting the update type to ASYNC
    'debug': False,
    'check_asp': True,  # Use ASP consistency check program
    'function_asp': True,  # Use ASP function program
    'all_opt': True,  # Show one or more solutions
    'labelling': False,
    'multiple_profiles': True,
    'compare_level_function': True,
    'exact_middle_function_determination': True,
    'ignore_warnings': False,
    'force_optimum': False,
    'show_solution_for_each_inconsistency': False,  # Show best solution for each consistency check even if it is not globally optimum
    'show_all_functions': False,
    'check_consistency': False  # Just check the consistency of the model and return
}
