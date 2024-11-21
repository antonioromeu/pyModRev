#!/bin/bash

SRC_DIR="./ModRev/src"
BASE_COMMAND="modrev"
FULL_COMMAND="$SRC_DIR/$BASE_COMMAND"
if [ ! -f "$SRC_DIR/$BASE_COMMAND" ]; then
    cd $SRC_DIR
    make
    cd ..
fi

EXAMPLES_DIR="examples"
RESULTS_DIR="results"
CSV_OUTPUT="modrev.csv"

if [ ! -d "$RESULTS_DIR" ]; then
    mkdir -p "$RESULTS_DIR"
fi
echo "model,obs_file_1,obs_file_2,obs_type,update_policy,results,time" > "$RESULTS_DIR/$CSV_OUTPUT"

run_command_one_obs() {
    local model=$1
    local obs_file=$2
    local obs_type=$3
    local update_policy=$4
    echo "Running: $FULL_COMMAND -m $model -obs $obs_file -ot $obs_type -up $update_policy -v 0"
    start_time=$(gdate +%s.%N)
    results=$(timeout 3600s $FULL_COMMAND -m "$model" -obs "$obs_file" -ot "$obs_type" -up "$update_policy" -v 0)
    end_time=$(gdate +%s.%N)
    execution_time=$(printf "%.6f" "$(echo "$end_time - $start_time" | bc)")
    echo "$model,$obs_file,\"No 2nd obs\",$obs_type,$update_policy,\"$results\",$execution_time" >> "$RESULTS_DIR/$CSV_OUTPUT"
}

run_command_two_obs() {
    local model=$1
    local obs_file_1=$2
    local obs_file_2=$3
    local obs_type=$4
    local update_policy=$5
    echo "Running: $FULL_COMMAND -m $model -obs $obs_file_1 $obs_file_2 -ot $obs_type -up $update_policy -v 0"
    start_time=$(gdate +%s.%N)
    results=$(timeout 3600s $FULL_COMMAND -m "$model" -obs "$obs_file_1" "$obs_file_2" -ot "$obs_type" -up "$update_policy" -v 0)
    end_time=$(gdate +%s.%N)
    execution_time=$(printf "%.6f" "$(echo "$end_time - $start_time" | bc)")
    echo "$model,$obs_file_1,$obs_file_2,$obs_type,$update_policy,\"$results\",$execution_time" >> "$RESULTS_DIR/$CSV_OUTPUT"
}

for network in examples/*/; do
    NON_CORRUPTED="${network}non_corrupted"
    CORRUPTED="${network}corrupted"
    OBS="${network}obs"

    # Check if required folders exist
    if [ ! -d "$NON_CORRUPTED" ] || [ ! -d "$CORRUPTED" ] || [ ! -d "$OBS" ]; then
        echo "Skipping $network: required folders missing."
        continue
    fi

    NON_CORRUPTED_MODEL=$(find "$NON_CORRUPTED" -type f)
    SS_FILE=$(find "$OBS/ss" -type f)
    TS_SYNC_FILES=($(find "$OBS/ts/ssync" -type f | sort -V))
    TS_ASYNC_FILES=($(find "$OBS/ts/async" -type f | sort -V))

    # Process non-corrupted model with 1 obs file
    for obs in "$SS_FILE" "${TS_SYNC_FILES[@]}" "${TS_ASYNC_FILES[@]}"; do
        if [[ $obs == *"/ss/"* ]]; then
            run_command_one_obs "$NON_CORRUPTED_MODEL" "$obs" "ss" "s"
        elif [[ $obs == *"/ssync/"* ]]; then
            run_command_one_obs "$NON_CORRUPTED_MODEL" "$obs" "ts" "s"
        elif [[ $obs == *"/async/"* ]]; then
            run_command_one_obs "$NON_CORRUPTED_MODEL" "$obs" "ts" "a"
        fi
    done

    # Process non-corrupted model with 2 obs files
    for obs in "${TS_SYNC_FILES[@]}" "${TS_ASYNC_FILES[@]}"; do
        if [[ $obs == *"/ssync/"* ]]; then
            run_command_two_obs "$NON_CORRUPTED_MODEL" "$SS_FILE" "$obs" "both" "s"
        elif [[ $obs == *"/async/"* ]]; then
            run_command_two_obs "$NON_CORRUPTED_MODEL" "$SS_FILE" "$obs" "both" "a"
        fi
    done

    # Process corrupted models with 1 obs file
    for corrupted_folder in "$CORRUPTED"/*; do
        if [ -d "$corrupted_folder" ]; then
            for model_file in "$corrupted_folder"/*; do
                if [[ $model_file == *"-net.lp" ]]; then
                    for obs in "$SS_FILE" "${TS_ASYNC_FILES[@]}" "${TS_SYNC_FILES[@]}"; do
                        if [[ $obs == *"/ss/"* ]]; then
                            run_command_one_obs "$model_file" "$obs" "ss" "s"
                        elif [[ $obs == *"/ssync/"* ]]; then
                            run_command_one_obs "$model_file" "$obs" "ts" "s"
                        elif [[ $obs == *"/async/"* ]]; then
                            run_command_one_obs "$model_file" "$obs" "ts" "a"
                        fi
                    done
                fi
            done
        fi
    done

    # Process corrupted models with 2 obs files
    for corrupted_folder in "$CORRUPTED"/*; do
        if [ -d "$corrupted_folder" ]; then
            for model_file in "$corrupted_folder"/*; do
                if [[ $model_file == *"-net.lp" ]]; then
                    for obs in "${TS_SYNC_FILES[@]}" "${TS_ASYNC_FILES[@]}"; do
                        if [[ $obs == *"/ssync/"* ]]; then
                            run_command_two_obs "$model_file" "$SS_FILE" "$obs" "both" "s"
                        elif [[ $obs == *"/async/"* ]]; then
                            run_command_two_obs "$model_file" "$SS_FILE" "$obs" "both" "a"
                        fi
                    done
                fi
            done
        fi
    done
done