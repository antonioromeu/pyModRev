from enum import Enum

class Inconsistencies(Enum):
    CONSISTENT = 0
    SINGLE_INC_GEN = 1
    SINGLE_INC_PART = 2
    DOUBLE_INC = 3

class UpdateType(Enum):
    ASYNC = 0
    SYNC = 1
    MASYNC = 2

# Verbose level
# 0 - machine style output (minimalistic easily parsable)
# 1 - machine style output (using set of sets)
# 2 - human readable output [default]
verbose = 2

version = '1.0.0'

update = UpdateType.ASYNC # Setting the update type to ASYNC

# Default known values
configuration = {
    'debug': False,
    'check_asp': True, # Use ASP consistency check program
    'function_asp': True, # Use ASP function program
    'all_opt': True, # Show one or more solutions
    'multiple_profiles': True,
    'compare_level_function': True,
    'exact_middle_function_determination': True,
    'ignore_warnings': False,
    'force_optimum': False,
    'show_solution_for_each_inconsistency': False, # Show best solution for each consistency check solution even if it is not globally optimum
    'check_consistency': False, # Just check the consistency of the model and return
    'asp_cc_base': './asp/base.lp',
    'asp_cc_ss': './asp/stable_state/core_ss.lp',
    'asp_cc_d': './asp/dynamic/core_ts.lp',
    'asp_cc_d_a': './asp/dyanmic/a_update.lp',
    'asp_cc_d_s': './asp/dyanmic/s_update.lp',
    'asp_cc_d_ma': './asp/dyanmic/ma_update.lp'
}