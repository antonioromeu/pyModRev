import pandas as pd
import os
import re
from collections import defaultdict

def parse_dnf(expression):
    return frozenset(frozenset(item.strip().strip('()').split(' && ')) for item in expression.split('||'))

def parse_repair_operations(input_string):
    repairs = defaultdict(lambda: defaultdict(set))
    if input_string == "This network is consistent!":
        return input_string
    # Split the input into nodes by "/"
    nodes = input_string.split("/")
    
    for node in nodes:
        if not node.strip():
            continue
        # Split node and its repair operations using "@"
        node_name, repair_operations = node.split("@", 1)
        # Split repair operations into sets separated by ";"
        repair_sets = repair_operations.split(";")
        for repair_set in repair_sets:
            # Split repair operations into individual blocks by ":"
            for operation in repair_set.split(":"):
                # Extract the operation type and details using regex
                match = re.match(r"(A|R|E|F),(.+)", operation)
                if not match:
                    continue
                op_type, details = match.groups()
                if op_type == "F":
                    repairs[node_name]["F"].add(parse_dnf(details))
                elif op_type in {"A", "R", "E"}:
                    edge = frozenset(details.split(","))
                    repairs[node_name][op_type].add(edge)
    return dict(repairs)

def count_repair_operations(input_string):
    operation_counts = defaultdict(int)
    if input_string == "This network is consistent!":
        return input_string
    # Split the input into nodes by "/"
    nodes = input_string.split("/")
    
    for node in nodes:
        if not node.strip():
            continue
        # Split node and its repair operations using "@"
        node_name, repair_operations = node.split("@", 1)
        # Split repair operations into sets separated by ";"
        repair_sets = repair_operations.split(";")
        for repair_set in repair_sets:
            # Split repair operations into individual blocks by ":"
            for operation in repair_set.split(":"):
                # Extract the operation type and details using regex
                match = re.match(r"(A|R|E|F),(.+)", operation)
                if not match:
                    continue
                op_type, details = match.groups()
                operation_counts[op_type] += 1
    return dict(operation_counts)

def compare_nested_dicts(dict1, dict2):
    if dict1 == "This network is consistent!" and dict2 == "This network is consistent!":
        return True
    if set(dict1.keys()) != set(dict2.keys()):
        return False
    for key in dict1:
        nested1 = dict1[key]
        nested2 = dict2[key]
        if nested1.keys() != nested2.keys():
            return False
        for subkey in nested1:
            if nested1[subkey] != nested2[subkey]:
                return False
    return True

# input1 = "cdc25@E,cdc25,cdc25/ste9@F,(cdc2_cdc13 && cdc2_cdc13_a && ste9 && pp) || (cdc2_cdc13 && ste9 && sk && pp) || (cdc2_cdc13_a && ste9 && sk) || (cdc2_cdc13 && cdc2_cdc13_a && sk && pp)/wee1_mik1@E,wee1_mik1,wee1_mik1/cdc2_cdc13@E,ste9,cdc2_cdc13:E,slp1,cdc2_cdc13/slp1@E,cdc2_cdc13_a,slp1/cdc2_cdc13_a@E,rum1,cdc2_cdc13_a:E,slp1,cdc2_cdc13_a/sk@E,start,sk"
# input2 = "cdc25@E,cdc25,cdc25/cdc2_cdc13@E,slp1,cdc2_cdc13;E,ste9,cdc2_cdc13/cdc2_cdc13_a@E,rum1,cdc2_cdc13_a;E,slp1,cdc2_cdc13_a/sk@E,start,sk/slp1@E,cdc2_cdc13_a,slp1/ste9@F,(cdc2_cdc13_a && sk && ste9) || (cdc2_cdc13 && cdc2_cdc13_a && pp && sk) || (cdc2_cdc13 && cdc2_cdc13_a && pp && ste9) || (cdc2_cdc13 && pp && sk && ste9)/wee1_mik1@E,wee1_mik1,wee1_mik1"
# print(compare_nested_dicts(parse_repair_operations(input1), parse_repair_operations(input2)))
# print(parse_repair_operations(input1))
# print(parse_repair_operations(input2))
# print(parse_repair_operations(input1) == parse_repair_operations(input2))
# print(count_repair_operations(input1))
# print(count_repair_operations(input2))
# print(count_repair_operations(input1) == count_repair_operations(input2))

# Load the CSV files
def load_csv_files(file_path_1, file_path_2):
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    file1 = current_script_path + file_path_1
    file2 = current_script_path + file_path_2
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    return df1, df2

def create_merged_file(dataframe_1, dataframe_2):
    # Merge the DataFrames on the specified columns
    merge_columns = ['model', 'obs_file_1', 'obs_file_2', 'obs_type', 'update_policy']
    merged_df = pd.merge(dataframe_1, dataframe_2, on=merge_columns, suffixes=('_file_1', '_file_2'))
    return merged_df

def compare_results(merged_df, output_file):
    # Compare the 'results' column
    merged_df['normalized_file_1'] = merged_df['results_file_1'].apply(lambda x: parse_repair_operations(x) if pd.notna(x) else x)
    merged_df['normalized_file_2'] = merged_df['results_file_2'].apply(lambda x: parse_repair_operations(x) if pd.notna(x) else x)
    merged_df['count_normalized_file_1'] = merged_df['results_file_1'].apply(lambda x: count_repair_operations(x) if pd.notna(x) else x)
    merged_df['count_normalized_file_2'] = merged_df['results_file_2'].apply(lambda x: count_repair_operations(x) if pd.notna(x) else x)
    merged_df['results_match'] = merged_df['normalized_file_1'] == merged_df['normalized_file_2']
    # merged_df['results_match'] = compare_nested_dicts(merged_df['normalized_file_1'], merged_df['normalized_file_2'])
    merged_df['count_results_match'] = merged_df['count_normalized_file_1'] == merged_df['count_normalized_file_2']
    merged_df.to_csv("merged_df.csv", index=False)
    row_count = merged_df.shape[0]
    print("Total number of rows:", row_count)
    count_na_normalized_file_1 = merged_df['normalized_file_1'].isna().sum()
    print("Total number of n.a. rows for file 1:", count_na_normalized_file_1)
    count_na_normalized_file_2 = merged_df['normalized_file_2'].isna().sum()
    print("Total number of n.a. rows for file 2:", count_na_normalized_file_2)

    count_na = merged_df[merged_df['normalized_file_1'].isna() | merged_df['normalized_file_2'].isna()].shape[0]
    print("Number of rows where n.a. is in either column of both files:", count_na)

    # Identify rows with mismatched results
    # mismatches = merged_df[~merged_df['results_match'] & ~merged_df['normalized_file1'].isna() & ~merged_df['normalized_file2'].isna()]
    mismatches = merged_df[~merged_df['results_match'] &
                        ~merged_df['normalized_file_1'].isna() &
                        ~merged_df['normalized_file_2'].isna() &
                        ~merged_df['count_results_match'] &
                        ~merged_df['count_normalized_file_1'].isna() &
                        ~merged_df['count_normalized_file_2'].isna()]

    # Output mismatched rows
    if mismatches.empty:
        print("All results match!")
    else:
        print("Mismatched rows:")
        print(mismatches)

    # mismatches[['model', 'obs_file_1', 'results_file_1', 'results_file_2', 'count_normalized_file_1', 'count_normalized_file_2']].to_csv("mismatched_rows_2.csv", index=False)
    mismatches.to_csv(output_file, index=False)

if __name__ == '__main__':
    results_dir = "results"
    csv_output = "mismatched_rows.csv"
    file_path_1 = "/../" + results_dir + "/pymodrev_corrupted.csv"
    file_path_2 = "/../" + results_dir + "/modrev_corrupted.csv"
    dataframe_1, dataframe_2 = load_csv_files(file_path_1, file_path_2)
    merged_df = create_merged_file(dataframe_1, dataframe_2)
    output_file = results_dir + "/" + csv_output
    compare_results(merged_df, output_file)