#!/bin/bash

# /usr/bin/python3 main.py -m examples/fissionYeastDavidich2008/corrupted/00/fissionYeastDavidich2008-0-0-0-1-net.lp -obs examples/fissionYeastDavidich2008/obs/ts/async/a_o1_t5.lp -ot ts -up a -v 2
# ./scripts/run_model.sh -n fissionYeastDavidich2008 -s 05 -f 24 -c -nc -no 1

BASE_COMMAND="/usr/bin/python3 main.py"
EXAMPLES_DIR="examples"
RESULTS_DIR="results"
CSV_OUTPUT="pymodrev_corrupted.csv"

run_command_one_obs() {
    local model=$1
    local obs_file=$2
    local obs_type=$3
    local update_policy=$4
    echo "Running: $BASE_COMMAND -m $model -obs $obs_file -ot $obs_type -up $update_policy -v 0"
    start_time=$(gdate +%s.%N)
    results=$(timeout 3600s $BASE_COMMAND -m "$model" -obs "$obs_file" -ot "$obs_type" -up "$update_policy" -v 0)
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
    echo "Running: $BASE_COMMAND -m $model -obs $obs_file_1 $obs_file_2 -ot $obs_type -up $update_policy -v 0"
    start_time=$(gdate +%s.%N)
    results=$(timeout 3600s $BASE_COMMAND -m "$model" -obs "$obs_file_1" "$obs_file_2" -ot "$obs_type" -up "$update_policy" -v 0)
    end_time=$(gdate +%s.%N)
    execution_time=$(printf "%.6f" "$(echo "$end_time - $start_time" | bc)")
    echo "$model,$obs_file_1,$obs_file_2,$obs_type,$update_policy,\"$results\",$execution_time" >> "$RESULTS_DIR/$CSV_OUTPUT"
}

if [ ! -d "$RESULTS_DIR" ]; then
    mkdir -p "$RESULTS_DIR"
fi
echo "model,obs_file_1,obs_file_2,obs_type,update_policy,results,time" > "$RESULTS_DIR/$CSV_OUTPUT"
input_network=""
start_folder=""
finish_folder=""
run_non_corrupted=0
run_corrupted=0
n_observations="0" # 0 for single and mix, 1 just single, 2 just mix
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--network)
            input_network=$2
            shift 2
            ;;
        -nc|--non_corrupted)
            run_non_corrupted=1
            shift 1
            ;;
        -c|--corrupted)
            run_corrupted=1
            shift 1
            ;;
        -s|--start)
            start_folder=$2
            shift 2
            ;;
        -f|--finish)
            finish_folder=$2
            shift 2
            ;;
        -no|--n_observations)
            n_observations=$2
            shift 2
            ;;
    esac
done

for network in examples/*/; do
    if [ -n "$input_network" ] && [[ $network != *"/$input_network/"* ]]; then
        continue
    fi

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

    if [[ $run_non_corrupted -eq 1 ]]; then
        # Process non-corrupted model with 1 obs file
        if [[ $n_observations == "0" || $n_observations == "1" ]]; then
            for obs in "$SS_FILE" "${TS_SYNC_FILES[@]}" "${TS_ASYNC_FILES[@]}"; do
                if [[ $obs == *"/ss/"* ]]; then
                    run_command_one_obs "$NON_CORRUPTED_MODEL" "$obs" "ss" "s"
                elif [[ $obs == *"/ssync/"* ]]; then
                    run_command_one_obs "$NON_CORRUPTED_MODEL" "$obs" "ts" "s"
                elif [[ $obs == *"/async/"* ]]; then
                    run_command_one_obs "$NON_CORRUPTED_MODEL" "$obs" "ts" "a"
                fi
            done
        fi

        # Process non-corrupted model with 2 obs files
        if [[ $n_observations == "0" || $n_observations == "2" ]]; then
            for obs in "${TS_SYNC_FILES[@]}" "${TS_ASYNC_FILES[@]}"; do
                if [[ $obs == *"/ssync/"* ]]; then
                    run_command_two_obs "$NON_CORRUPTED_MODEL" "$SS_FILE" "$obs" "both" "s"
                elif [[ $obs == *"/async/"* ]]; then
                    run_command_two_obs "$NON_CORRUPTED_MODEL" "$SS_FILE" "$obs" "both" "a"
                fi
            done
        fi
    fi

    if [[ $run_corrupted -eq 1 ]]; then
        # Process corrupted models with 1 obs file
        if [[ $n_observations == "0" || $n_observations == "1" ]]; then
            for corrupted_folder in "$CORRUPTED"/*; do
                folder_number="${corrupted_folder: -2}"
                if [ -n "$start_folder" ] && [ -n "$finish_folder" ] && !(( 10#$folder_number >= 10#$start_folder && 10#$folder_number <= 10#$finish_folder )); then
                    continue
                fi
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
        fi

        # Process corrupted models with 2 obs files
        if [[ $n_observations == "0" || $n_observations == "2" ]]; then
            for corrupted_folder in "$CORRUPTED"/*; do
                folder_number="${corrupted_folder: -2}"
                if [ -n "$start_folder" ] && [ -n "$finish_folder" ] && !(( 10#$folder_number >= 10#$start_folder && 10#$folder_number <= 10#$finish_folder )); then
                    continue
                fi
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
        fi
    fi
done