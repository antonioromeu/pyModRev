#!/bin/bash

# Function to run a script and log its output
run_script() {
  script_name=$1
  log_file=$2

  echo "Starting $script_name..."
  ./$script_name > "$log_file" 2>&1 &
}

# Define scripts and log files
declare -a scripts=("script1.sh" "script2.sh" "script3.sh")
log_dir="logs"

# Create a directory for logs if it doesn't exist
mkdir -p "$log_dir"

# Run scripts in parallel
for script in "${scripts[@]}"; do
  log_file="$log_dir/${script%.sh}.log"
  run_script "$script" "$log_file"
done

# Wait for all scripts to complete
echo "Waiting for all scripts to complete..."
wait
echo "All scripts completed."

# Optional: Print a summary
echo "Script execution summary:"
for script in "${scripts[@]}"; do
  log_file="$log_dir/${script%.sh}.log"
  echo "Log for $script:"
  cat "$log_file"
done
