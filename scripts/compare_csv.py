import pandas as pd
import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

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

def compare_nested_dicts(results_1, results_2):
    if pd.isna(results_1) and pd.isna(results_2):
        return True
    elif pd.isna(results_1) and pd.notna(results_2) or \
        pd.notna(results_1) and pd.isna(results_2):
        return False
    elif results_1 == "This network is consistent!" and results_2 == "This network is consistent!":
        return True
    if set(results_1.keys()) != set(results_2.keys()):
        return False
    for key in results_1:
        nested1 = results_1[key]
        nested2 = results_2[key]
        if nested1.keys() != nested2.keys():
            return False
        for subkey in nested1:
            if nested1[subkey] != nested2[subkey]:
                return False
    return True

def load_csv_files(file_path_1, file_path_2):
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    file1 = current_script_path + file_path_1
    file2 = current_script_path + file_path_2
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    return df1, df2

def create_merged_file(dataframe_1, dataframe_2):
    merge_columns = ['model', 'obs_file_1', 'obs_file_2', 'obs_type', 'update_policy']
    merged_df = pd.merge(dataframe_1, dataframe_2, on=merge_columns, suffixes=('_file_1', '_file_2'))
    return merged_df

def compare_results(merged_df, merged_output_file, matched_output_file, mismatched_output_file):
    merged_df['parsed_results_file_1'] = merged_df['results_file_1'].apply(lambda x: parse_repair_operations(x) if pd.notna(x) else x)
    merged_df['parsed_results_file_2'] = merged_df['results_file_2'].apply(lambda x: parse_repair_operations(x) if pd.notna(x) else x)
    
    merged_df['count_parsed_results_file_1'] = merged_df['results_file_1'].apply(lambda x: count_repair_operations(x) if pd.notna(x) else x)
    merged_df['count_parsed_results_file_2'] = merged_df['results_file_2'].apply(lambda x: count_repair_operations(x) if pd.notna(x) else x)
    
    # merged_df['results_match'] = merged_df['parsed_results_file_1'] == merged_df['parsed_results_file_2']
    merged_df['results_match'] = merged_df.apply(
        lambda row: compare_nested_dicts(row['parsed_results_file_1'], row['parsed_results_file_2']),
        axis=1
    )
    merged_df['count_results_match'] = merged_df['count_parsed_results_file_1'] == merged_df['count_parsed_results_file_2']
    
    row_count = merged_df.shape[0]
    print("Number of rows for merged dataframe:", row_count)
    count_na_parsed_results_file_1 = merged_df['parsed_results_file_1'].isna().sum()
    print("Number of NA parsed results for file 1:", count_na_parsed_results_file_1)
    count_na_parsed_results_file_2 = merged_df['parsed_results_file_2'].isna().sum()
    print("Number of NA parsed results for file 2:", count_na_parsed_results_file_2)
    # count_na = merged_df[merged_df['parsed_results_file_1'].isna() | merged_df['parsed_results_file_2'].isna()].shape[0]
    # print("Number of rows where NA is in either parsed column of both files:", count_na)
    count_greater = (
        (merged_df['time_file_1'] > merged_df['time_file_2']) &
        (merged_df['time_file_1'] < 3600) &
        (merged_df['time_file_2'] < 3600)
    ).sum()
    count_lower = (
        (merged_df['time_file_1'] < merged_df['time_file_2']) &
        (merged_df['time_file_1'] < 3600) &
        (merged_df['time_file_2'] < 3600)
    ).sum()
    print(f"Times where time_file_1 > time_file_2: {count_greater}")
    print(f"Times where time_file_1 < time_file_2: {count_lower}")

    # mismatches = merged_df[~merged_df['results_match'] &
    #                     ~merged_df['parsed_results_file_1'].isna() &
    #                     ~merged_df['parsed_results_file_2'].isna() &
    #                     ~merged_df['count_results_match'] &
    #                     ~merged_df['count_parsed_results_file_1'].isna() &
    #                     ~merged_df['count_parsed_results_file_2'].isna()]

    matches = merged_df[merged_df['results_match'] |
                        merged_df['count_results_match']]

    mismatches = merged_df[~merged_df['results_match'] &
                        ~merged_df['count_results_match']]

    # na_or = merged_df[merged_df['parsed_results_file_1'].isna() |
    #                     merged_df['parsed_results_file_2'].isna() |
    #                     merged_df['count_parsed_results_file_1'].isna() |
    #                     merged_df['count_parsed_results_file_2'].isna()]
    
    # na_and = merged_df[merged_df['parsed_results_file_1'].isna() &
    #                 merged_df['parsed_results_file_2'].isna()]
    
    # na_exclusive = pd.merge(na_and, na_or, on=['model', 'obs_file_1', 'obs_file_2', 'obs_type', 'update_policy'], how='inner')

    if mismatches.empty:
        print("All results match")
    else:
        print("Mismatched rows saved to file")

    merged_df.to_csv(merged_output_file, index=False)
    matches.to_csv(matched_output_file, index=False)
    mismatches.to_csv(mismatched_output_file, index=False)

# def categorize_obs(obs):
#     if 'async/a_o1' in obs:
#         return 'async/a_o1'
#     elif 'async/a_o3' in obs:
#         return 'async/a_o3'
#     elif 'async/a_o5' in obs:
#         return 'async/a_o5'
#     elif 'ssync/s_o1' in obs:
#         return 'ssync/s_o1'
#     elif 'ssync/s_o3' in obs:
#         return 'ssync/s_o3'
#     elif 'ssync/s_o5' in obs:
#         return 'ssync/s_o5'
#     elif 'attractors' in obs:
#         return 'attractors'

def categorize_obs(obs):
    if 'async/a_o3_t3' in obs:
        return 'async/a_o3_t3'
    elif 'async/a_o3_t20' in obs:
        return 'async/a_o3_t20'
    elif 'ssync/s_o3_t3' in obs:
        return 'ssync/s_o3_t3'
    elif 'ssync/s_o3_t20' in obs:
        return 'ssync/s_o3_t20'
    elif 'attractors' in obs:
        return 'attractors'

def generate_boxplot(dataframe, model):
    dataframe['group'] = dataframe['obs_file_1'].apply(categorize_obs)
    melted_data = dataframe.melt(
        id_vars=['group'],
        value_vars=['time_file_1', 'time_file_2'],
        var_name='time_file',
        value_name='time'
    )
    plt.figure(figsize=(12, 6))
    sns.boxplot(
        data=melted_data,
        x='group',
        y='time',
        hue='time_file',
        palette='muted'
    )
    plt.yscale('log')
    handles, labels = plt.gca().get_legend_handles_labels()
    labels = ['pyModRev', 'ModRev'] # Set custom aliases
    plt.legend(handles, labels, title="Software")
    plt.title(f"Execution times grouped by observation category for {model} model")
    plt.xlabel("Observation category")
    plt.ylabel("Time in seconds")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    fig_output = f"/Users/antonioromeu/Documents/PyModRev.nosync/results/{model}/box_plot.png"
    plt.savefig(fig_output)

if __name__ == '__main__':
    results_dir = "results"
    merged_csv_output = "merged_rows.csv"
    matched_csv_output = "matched_rows.csv"
    mismatched_csv_output = "mismatched_rows.csv"
    models = ['boolean_cell_cycle', 'fissionYeastDavidich2008', 'SP_1cell', 'TCRsig40', 'thNetworkGarg2007']
    for model in models:
        # if model != 'fissionYeastDavidich2008':
        #     continue
        file_path_1 = "/../" + results_dir + "/" + model + "/" + "pymodrev_corrupted.csv"
        file_path_2 = "/../" + results_dir + "/" + model + "/" + "modrev_corrupted.csv"
        merged_output_file = results_dir + "/" + model + "/" + merged_csv_output
        matched_output_file = results_dir + "/" + model + "/" + matched_csv_output
        mismatched_output_file = results_dir + "/" + model + "/" + mismatched_csv_output
        dataframe_1, dataframe_2 = load_csv_files(file_path_1, file_path_2)
        merged_df = create_merged_file(dataframe_1, dataframe_2)
        compare_results(merged_df, merged_output_file, matched_output_file, mismatched_output_file)
        generate_boxplot(merged_df, model)

# input1 = "cdc25@E,cdc25,cdc25/ste9@F,(cdc2_cdc13 && cdc2_cdc13_a && ste9 && pp) || (cdc2_cdc13 && ste9 && sk && pp) || (cdc2_cdc13_a && ste9 && sk) || (cdc2_cdc13 && cdc2_cdc13_a && sk && pp)/wee1_mik1@E,wee1_mik1,wee1_mik1/cdc2_cdc13@E,ste9,cdc2_cdc13:E,slp1,cdc2_cdc13/slp1@E,cdc2_cdc13_a,slp1/cdc2_cdc13_a@E,rum1,cdc2_cdc13_a:E,slp1,cdc2_cdc13_a/sk@E,start,sk"
# input2 = "cdc25@E,cdc25,cdc25/cdc2_cdc13@E,slp1,cdc2_cdc13;E,ste9,cdc2_cdc13/cdc2_cdc13_a@E,rum1,cdc2_cdc13_a;E,slp1,cdc2_cdc13_a/sk@E,start,sk/slp1@E,cdc2_cdc13_a,slp1/ste9@F,(cdc2_cdc13_a && sk && ste9) || (cdc2_cdc13 && cdc2_cdc13_a && pp && sk) || (cdc2_cdc13 && cdc2_cdc13_a && pp && ste9) || (cdc2_cdc13 && pp && sk && ste9)/wee1_mik1@E,wee1_mik1,wee1_mik1"
# print(compare_nested_dicts(parse_repair_operations(input1), parse_repair_operations(input2)))
# print(parse_repair_operations(input1))
# print(parse_repair_operations(input2))
# print(parse_repair_operations(input1) == parse_repair_operations(input2))
# print(count_repair_operations(input1))
# print(count_repair_operations(input2))
# print(count_repair_operations(input1) == count_repair_operations(input2))