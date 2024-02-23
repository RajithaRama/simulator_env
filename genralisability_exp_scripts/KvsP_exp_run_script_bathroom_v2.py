import itertools
import os
import sys
import shutil
import time
import json
import genralisability_exp_scripts.modify_case_base_v2 as modify_case_base
import genralisability_exp_scripts.test_run as test_run
import numpy as np

data_dir = "Data"

np.random.seed(42)

FULL_KB_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_bathroom.json'
FULL_KB_BAK_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_bathroom_temp_bak.json'

# k = [2, 3, 5, 8]
# percentages = [0.1, 0.25, 0.5, 0.8, 1]
# percentages = [1]
# scenarios = ['Bathroom_Scn1', 'Bathroom_Scn3', 'Bathroom_Scn4', 'Bathroom_Scn5', 'Bathroom_Scn6', 'Bedroom_Scn1',
#              'Bedroom_Scn2', 'Bedroom_Scn3']

bathroom_scenarios = ['Bathroom_Scn1', 'Bathroom_Scn3', 'Bathroom_Scn4', 'Bathroom_Scn5', 'Bathroom_Scn6']
bathroom_scenarios_normal = ['Bathroom_Scn1', 'Bathroom_Scn3']
bathroom_scenarios_special = ['Bathroom_Scn4', 'Bathroom_Scn5', 'Bathroom_Scn6']

bedroom_scenarios = ['Bedroom_Scn1', 'Bedroom_Scn2', 'Bedroom_Scn3']
bedroom_scenarios_normal = ['Bedroom_Scn1']
bedroom_scenarios_special = ['Bedroom_Scn2', 'Bedroom_Scn3']

file_list = os.listdir(os.path.join('experiments_cmd', 'bathroom_dilemma_PSRB'))


# n = 0

# for k_value in k:
#     for percentage in percentages:
# for i in range(len(scenarios)):
#     for comb in itertools.combinations(scenarios, i + 1):
#         print(comb)
#         n += 1

# print(n) # 5100 combinations if ran all


# n = 0
#
# for k_value in k:
#     for percentage in percentages:
#         for bathroom_normal in bathroom_scenarios_normal:
#             for bathroom_special in bathroom_scenarios_special:
#                 for bedroom_normal in bedroom_scenarios_normal:
#                     for bedroom_special in bedroom_scenarios_special:
#                         print([bathroom_normal, bathroom_special, bedroom_normal, bedroom_special])
#                         n += 1
#
# print(n) # 240 combinations if ran all


# variation_0_bathroom = list(itertools.combinations(bathroom_scenarios, 4)) # all bathroom scenarios holding 1 off
# variation_0_bedroom = list(itertools.combinations(bedroom_scenarios, 2)) # all bedroom scenarios holding 1 off
#
# variation_1 = []  # 2 variations from each dilemma ( 1- normal and 1-special)
# for bathroom_normal in bathroom_scenarios_normal:
#     for bathroom_special in bathroom_scenarios_special:
#         for bedroom_normal in bedroom_scenarios_normal:
#             for bedroom_special in bedroom_scenarios_special:
#                 variation_1.append([bathroom_normal, bathroom_special, bedroom_normal, bedroom_special])
#
# # print(len(variation_1)) # 12
#
# variation_2 = [bathroom_scenarios, bedroom_scenarios]  # only variations from 1 dilemma
#
# variation_3 = [bathroom_scenarios_normal+bedroom_scenarios_special, bathroom_scenarios_special+bedroom_scenarios_normal]  # only normal in one dilemma and special in other

def run_experiment(spec_json, cases_to_run, iterations=1):

    spec = json.load(open(spec_json, 'r'))

    k = spec['k_range']
    percentages = spec['p_range']
    scenarios_in_kb = spec['scenarios_in_kb']
    experiment = spec['experiment_name']
    file_list = cases_to_run
    # file_list = list(itertools.chain.from_iterable(file_list))

    # print(file_list)

    # measuring the time taken for tests.
    st = time.time()

    # temp backup full knowledge base
    shutil.copyfile(FULL_KB_PATH, FULL_KB_BAK_PATH)

    for k_value in k:
        modify_case_base.dump_k_value(k_value)
        for percentage in percentages:
            # variation 0
            cond_run_start = time.time()
            arr_number_of_cases_in_kb = []
            for i in range(iterations):
                number_of_cases_in_kb = modify_case_base.generate_KB_json(scenarios=scenarios_in_kb, percentage=percentage, KB_path=FULL_KB_PATH)
                for file_list_item in file_list:
                    for case in file_list_item[1]:
                        if case.endswith('.py'):
                            test_run.run_case(dir=os.path.join(*file_list_item[0]), case_name=case,
                                              experiment=experiment,
                                              condition=str(k_value) + '_' + str(int(percentage * 100)))
                arr_number_of_cases_in_kb.append(number_of_cases_in_kb)
            cond_run_end = time.time()

            json.dump({'k': k_value, 'percentage': percentage, 'scenarios': scenarios_in_kb, 'cond_run_time': cond_run_end - cond_run_start,
                       'number_of_cases_in_kb': sum(arr_number_of_cases_in_kb)/len(arr_number_of_cases_in_kb)},
                      open(os.path.join(data_dir, experiment, str(int(k_value)) + '_' + str(int(percentage * 100)), 'cond_run_time.json'), 'w'))

    # resetting full knowledge base
    shutil.copyfile(FULL_KB_BAK_PATH, FULL_KB_PATH)

    et = time.time()

    print('Time taken: ', et - st, ' seconds')
    json.dump({'total_run_time': et - st}, open(os.path.join(data_dir, experiment, 'total_run_time.json'), 'w'))


if __name__ == '__main__':
    spec_json = sys.argv[1]
    spec = json.load(open(spec_json, 'r'))

    file_list = [] #(scn_dir, os.listdir(os.path.join(*scn_dir))) for scn_dir in spec['scn_dirs']]
    for scn_dir in spec['scn_dirs']:
        scn_dir_files = os.listdir(os.path.join(*scn_dir))
        scn_dir_files = [i for i in scn_dir_files if i.endswith('.py')]
        file_list.append((scn_dir, scn_dir_files))

    run_experiment(spec_json, file_list, iterations=5)
