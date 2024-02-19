import ast
import json
import os
import shutil
import random

import pandas as pd
import numpy as np

np.random.seed(42)

CASE_BASE = 'ethical_governor/blackboard/commonutils/cbr/data_medication.xlsx'
KB_JSON_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_medication.json'
SCN_RANGES_JSON_PATH = 'ethical_governor/blackboard/commonutils/cbr/scenario_ranges_medication.json'


def str_to_list(cell):
    if cell is not None:
        # print(type(cell))
        var = ast.literal_eval(cell)
    else:
        var = None
    return var


def generate_KB_json(scenarios, percentage=1, KB_path=KB_JSON_PATH):

    KB_JSON_PATH = KB_path
    df = pd.read_excel(CASE_BASE, header=0, index_col=None) # , "not_follow_locations": list,  "instructions_given": list})
    # df.astype({"not_follow_locations": list,  "instructions_given": list})

    # Compile the requested scenarios cases by dropping the rest and sampling the percentage of cases
    sampled_df = pd.DataFrame(columns=df.columns)
    scn_ranges = json.load(open(SCN_RANGES_JSON_PATH, 'r'))
    for scn, boundaries in scn_ranges.items():
        if scn not in scenarios:
            # start = int(boundaries['start'])
            # end = int(boundaries['end'])
            # case_range = list(range(start, end + 1))
            # df = df[~df['case_id'].isin(case_range)]
            continue
        else:
            start = int(boundaries['start'])
            end = int(boundaries['end'])
            case_range = list(range(start, end + 1))
            if len(sampled_df) == 0:
                sampled_df = df[df['case_id'].isin(case_range)].sample(frac=percentage).sort_values(by=['case_id'])
            else:
                sampled_df = pd.concat([sampled_df, df[df['case_id'].isin(case_range)].sample(frac=percentage).sort_values(by=['case_id'])], sort=False)



    # remove duplicates
    feature_names = sampled_df.columns.tolist()
    feature_names.remove("case_id")
    sampled_df.drop_duplicates(subset=feature_names, keep='first', inplace=True)

    # # changing dtype to lists
    # sampled_df['not_follow_locations'] = sampled_df['not_follow_locations'].apply(str_to_list)
    # sampled_df['instructions_given'] = sampled_df['instructions_given'].apply(str_to_list)

    # print(df)
    print(sampled_df.dtypes)

    sampled_df.to_json(KB_JSON_PATH, orient='records', indent=4)


    # returning kb information
    number_of_cases = len(sampled_df)
    return number_of_cases


def dump_k_value(k_value):
    json.dump(k_value, open('genralisability_exp_scripts/k_value.json', 'w'))


if __name__ == '__main__':

    # dump k value
    dump_k_value(3)

    KB_JSON_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_test_medication.json'
    generate_KB_json(['Scn1', 'Scn3', 'Scn4', 'Scn5'], KB_path=KB_JSON_PATH)

    print('test 1 done')

    # generate_KB_json(
    #     ['Bathroom_Scn1', 'Bathroom_Scn3', 'Bathroom_Scn4', 'Bedroom_Scn1', 'Bedroom_Scn2'], percentage=0.5)
    #
    # print('test 2 done')