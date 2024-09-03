#!/bin/sh
python3 -m network.tests.test_edge # TODO understand why calling it like this works
python3 -m network.tests.test_function
# python3 -m network.tests.test_inconsistency_solution
# python3 -m network.tests.test_inconsistent_node
python3 -m network.tests.test_network
python3 -m network.tests.test_node
python3 -m network.tests.test_repair_set

# python3 -m network.tests.test_pfh_clause
# python3 -m network.tests.test_pfh_function
# python3 -m network.tests.test_pfh_hassediagram
# python3 -m network.tests.test_pfh_powerset

# chmod 755 run_tests.sh
# ./run_tests.sh