#!/bin/bash

PYTHON_PATH="/usr/bin/python3"
SCRIPT_PATH="main.py"
EXAMPLES_DIR="examples"
RESULTS_DIR="results"
CSV_OUTPUT="obs_results.csv"

echo "model,obs,ot,up,results,time" > "$RESULTS_DIR/$CSV_OUTPUT"

for model_dir in "$EXAMPLES_DIR"/*; do
    if [[ -d "$model_dir" ]]; then
        model_file=$(find "$model_dir" -maxdepth 1 -name "*.lp" | head -n 1)
        # ss_dir="$model_dir/obs/ss"
        ts_dir="$model_dir/obs/ts"
        if [[ -f "$model_file" && -d "$ts_dir" ]]; then
            for mode in "async" "ssync"; do
                mode_dir="$ts_dir/$mode"
                if [[ "$mode" == "async" ]]; then
                    up_flag="a"
                else
                    up_flag="s"
                fi
                for obs_file in "$mode_dir"/*.lp; do
                    if [[ -f "$obs_file" ]]; then
                        echo "Running model: $model_file with observation: $obs_file"
                        start_time=$(gdate +%s.%N)
                        result=$($PYTHON_PATH "$SCRIPT_PATH" "$model_file" -obs "$obs_file" -ot ts -up "$up_flag")
                        end_time=$(gdate +%s.%N)
                        execution_time=$(printf "%.6f" "$(echo "$end_time - $start_time" | bc)")
                        echo "$model_file,$obs_file,ts,$up_flag,\"$result\",$execution_time" >> "$RESULTS_DIR/$CSV_OUTPUT"
                    fi
                done
            done
        else
            echo "Model file or ts directory missing in $model_dir"
        fi
    fi
done