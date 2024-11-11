#!/bin/sh

PYTHON_PATH="/usr/bin/python3"
SCRIPT_PATH="main.py"
NETWORK_DIR="network"
TESTS_DIR="tests"

for folder in "$NETWORK_DIR"/*; do
    if [ -d "$folder/"$NETWORK_DIR"/tests" ]; then
        for test in "$folder/tests"/*; do
            echo "Running test: $test"
            $($PYTHON_PATH -m "$folder"/"$test")
        done
    fi
done

# python3 -m network.tests.test_edge
# python3 -m network.tests.test_function
# python3 -m network.tests.test_inconsistency_solution
# python3 -m network.tests.test_inconsistent_node
# python3 -m network.tests.test_network
# python3 -m network.tests.test_node
# python3 -m network.tests.test_repair_set

# python3 -m network.tests.test_pfh_clause
# python3 -m network.tests.test_pfh_function
# python3 -m network.tests.test_pfh_hassediagram
# python3 -m network.tests.test_pfh_powerset

# chmod 755 run_tests.sh
# ./run_tests.sh