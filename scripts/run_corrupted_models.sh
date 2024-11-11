#!/bin/bash

PYTHON_PATH="/usr/bin/python3"
SCRIPT_PATH="main.py"
EXAMPLES_DIR="examples"
RESULTS_DIR="results"
CSV_OUTPUT="corrupted_results.csv"

echo "model,folder,obs,ot,up,results,time" > "$RESULTS_DIR/$CSV_OUTPUT"

for model_dir in "$EXAMPLES_DIR"/*; do
    if [[ -d "$model_dir" ]]; then
        model_file=$(find "$model_dir" -maxdepth 1 -name "*.lp" | head -n 1)
        corrupted_dir="$model_dir/corrupted"
        if [[ -d "$corrupted_dir" ]]; then
            for sub_dir in "$corrupted_dir"/[0-9][0-9]; do
                ot_flag="ss"
                up_flag="s"
                if [[ -d "$sub_dir" ]]; then
                    model_files=($(find "$sub_dir" -maxdepth 1 -name "*-net.lp"))
                    folder_number=$(basename "$sub_dir")
                    for model_file in "${model_files[@]}"; do
                        prefix="${model_file%-net.lp}"
                        obs_file="${prefix}-net-att.lp"
                        if [[ -f "$obs_file" ]]; then
                            echo "Running corrupted model: $model_file with observation: $obs_file"
                            start_time=$(gdate +%s.%N)
                            results=$($PYTHON_PATH "$SCRIPT_PATH" "$model_file" -obs "$obs_file" -ot "$ot_flag" -up "$up_flag" | head -n 1)
                            end_time=$(gdate +%s.%N)
                            execution_time=$(printf "%.6f" "$(echo "$end_time - $start_time" | bc)")
                            echo "$model_file,$folder_number,$obs_file,$ot_flag,$up_flag,\"$results\",$execution_time" >> "$RESULTS_DIR/$CSV_OUTPUT"
                        else
                            echo "Observation file not found for model: $model_file"
                        fi
                    done
                fi
            done
        fi
    fi
done