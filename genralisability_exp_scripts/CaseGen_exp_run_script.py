import itertools
import os
import shutil
import time
import json
import sys
import genralisability_exp_scripts.modify_case_base as modify_case_base
import genralisability_exp_scripts.test_run as test_run
import genralisability_exp_scripts.KvsP_exp_run_script_bedroom as KvsP_exp_run_script_bedroom

FULL_KB_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_bathroom.json'
FULL_KB_BAK_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_bathroom_temp_bak.json'

# k = [2, 3, 5, 8]
# percentages = [0.1, 0.25, 0.5, 0.8, 1]
# percentages = [1]
# scenarios = ['Bathroom_Scn1', 'Bathroom_Scn3', 'Bathroom_Scn4', 'Bathroom_Scn5', 'Bathroom_Scn6', 'Bedroom_Scn1',
#              'Bedroom_Scn2', 'Bedroom_Scn3']

data_dir = "Data"

bathroom_scenarios = ['Bathroom_Scn1', 'Bathroom_Scn3', 'Bathroom_Scn4', 'Bathroom_Scn5', 'Bathroom_Scn6']
bathroom_scenarios_normal = ['Bathroom_Scn1', 'Bathroom_Scn3']
bathroom_scenarios_special = ['Bathroom_Scn4', 'Bathroom_Scn5', 'Bathroom_Scn6']

bedroom_scenarios = ['Bedroom_Scn1', 'Bedroom_Scn2', 'Bedroom_Scn3']
bedroom_scenarios_normal = ['Bedroom_Scn1']
bedroom_scenarios_special = ['Bedroom_Scn2', 'Bedroom_Scn3']

# file_list = os.listdir(os.path.join('experiments_cmd', 'bathroom_dilemma_PSRB'))

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


###### Method 1 ###############
variation_0_bathroom = list(itertools.combinations(bathroom_scenarios, 4))  # all bathroom scenarios holding 1 off
variation_0_bedroom = list(itertools.combinations(bedroom_scenarios, 2))  # all bedroom scenarios holding 1 off

variation_1 = []  # 2 variations from each dilemma ( 1- normal and 1-special)
for bathroom_normal in bathroom_scenarios_normal:
    for bathroom_special in bathroom_scenarios_special:
        for bedroom_normal in bedroom_scenarios_normal:
            for bedroom_special in bedroom_scenarios_special:
                variation_1.append([bathroom_normal, bathroom_special, bedroom_normal, bedroom_special])

# print(len(variation_1)) # 12

variation_2 = [bathroom_scenarios, bedroom_scenarios]  # only variations from 1 dilemma

variation_3 = [bathroom_scenarios_normal + bedroom_scenarios_special,
               bathroom_scenarios_special + bedroom_scenarios_normal]  # only normal in one dilemma and special in other
#######################################

################### Medthod 2 #############################

# n = 0

# for k_value in k:
#     for percentage in percentages:
# for i in range(len(scenarios)):
#     for comb in itertools.combinations(scenarios, i + 1):
#         print(comb)
#         n += 1

# print(n) # 5100 combinations if ran all


scenario_casename_map = {'Bathroom_Scn1': ['bathroom_dilemma_case1_PSRB.py', 'bathroom_dilemma_case1_PSRB_autonomy.py',
                                           'bathroom_dilemma_case1_PSRB_balanced.py'],
                         'Bathroom_Scn3': ['bathroom_dilemma_case2_PSRB.py', 'bathroom_dilemma_case2_PSRB_autonomy.py',
                                           'bathroom_dilemma_case2_PSRB_balanced.py', 'bathroom_dilemma_case3_PSRB.py',
                                           'bathroom_dilemma_case3_PSRB_autonomy.py',
                                           'bathroom_dilemma_case3_PSRB_balanced.py'],
                         'Bathroom_Scn4': ['bathroom_dilemma_case4_PSRB.py', 'bathroom_dilemma_case4_PSRB_autonomy.py',
                                           'bathroom_dilemma_case4_PSRB_balanced.py'],
                         'Bathroom_Scn5': ['bathroom_dilemma_case5_PSRB.py', 'bathroom_dilemma_case5_PSRB_autonomy.py',
                                           'bathroom_dilemma_case5_PSRB_balanced.py'],
                         'Bathroom_Scn6': ['bathroom_dilemma_case6_PSRB.py', 'bathroom_dilemma_case6_PSRB_autonomy.py',
                                           'bathroom_dilemma_case6_PSRB_balanced.py'],
                         'Bedroom_Scn1': ['bedroom_dilemma_case1_PSRB.py', 'bedroom_dilemma_case1_PSRB_autonomy.py',
                                          'bedroom_dilemma_case1_PSRB_balanced.py'],
                         'Bedroom_Scn2': ['bedroom_dilemma_case2_PSRB.py', 'bedroom_dilemma_case2_PSRB_autonomy.py',
                                          'bedroom_dilemma_case2_PSRB_balanced.py'],
                         'Bedroom_Scn3': ['bedroom_dilemma_case3_PSRB.py', 'bedroom_dilemma_case3_PSRB_autonomy.py',
                                          'bedroom_dilemma_case3_PSRB_balanced.py']}

scnario_dir_name_ids_map = {'Bathroom_Scn1': 'BT1',
                            'Bathroom_Scn3': 'BT3',
                            'Bathroom_Scn4': 'BT4',
                            'Bathroom_Scn5': 'BT5',
                            'Bathroom_Scn6': 'BT6',
                            'Bedroom_Scn1': 'BD1',
                            'Bedroom_Scn2': 'BD2',
                            'Bedroom_Scn3': 'BD3'}


def run_combinations(spec_json):
    spec = json.load(open(spec_json, 'r'))

    k = spec['k_range']
    percentages = spec['p_range']
    k_start_index = spec['k_start_index']
    p_start_index = spec['p_start_index']
    k_end_index = spec['k_end_index']
    p_end_index = spec['p_end_index']

    scenarios = spec['scenarios']
    experiment = spec['experiment_name']

    scn_dirs = spec['scn_dirs']
    combination_lengths = spec['length_of_combinations']
    combinations = []

    for i in combination_lengths:
        for comb in itertools.combinations(scenarios, i):
            combinations.append(comb)

    st = time.time()
    for combination in combinations:
        print(combination)
        st_combination = time.time()
        spec_name = '_'.join([scnario_dir_name_ids_map[i] for i in combination])
        spec_json_path = dump_spec(spec_name=spec_name, k=k, percentages=percentages, k_start_index=k_start_index,
                  p_start_index=p_start_index, k_end_index=k_end_index, p_end_index=p_end_index,
                  scenarios_in_kb=combination, experiment=os.path.join(experiment, spec_name), scn_dirs=scn_dirs)

        file_list = []
        omitted_cases = []
        all_relvant_cases = []
        for scn in scenarios:
            all_relvant_cases.extend(scenario_casename_map[scn])

        for scn in combination:
            omitted_cases.extend(scenario_casename_map[scn])

        for scn_dir in scn_dirs:
            scn_dir_files = os.listdir(os.path.join(*scn_dir))
            scn_dir_files = [i for i in scn_dir_files if i.endswith('.py') and (i not in omitted_cases) and (i in all_relvant_cases)]

            file_list.append((scn_dir, scn_dir_files))

        KvsP_exp_run_script_bedroom.run_experiment(spec_json_path, file_list)
        et_combination = time.time()
        json.dump({'combination_run_time': et_combination - st_combination, 'combination': combination, 'tested_file_list': file_list},
                  open(os.path.join(data_dir, experiment, spec_name, 'combination_run_data.json'), 'w'))

    et_experiment = time.time()
    json.dump({'experiment_run_time': et_experiment - st, 'experiment': experiment, 'tested_combinations': combinations},
              open(os.path.join(data_dir, experiment, 'experiment_run_data_'+time.strftime("%Y%m%d-%H%M%S")+'.json'), 'w'))


def dump_spec(spec_name, k, percentages, k_start_index, p_start_index, k_end_index, p_end_index, scenarios_in_kb,
              experiment, scn_dirs):

    KvP_spec = {
        'k_range': k[k_start_index:k_end_index],
        'p_range': percentages[p_start_index:p_end_index],
        'scenarios_in_kb': scenarios_in_kb,
        'experiment_name': experiment
    }
    if not os.path.exists(os.path.join(data_dir, experiment)):
        os.makedirs(os.path.join(data_dir, experiment))
    json.dump(KvP_spec, open(os.path.join(data_dir, experiment, spec_name + '_spec.json'), 'w'))

    return os.path.join(data_dir, experiment, spec_name + '_spec.json')


if __name__ == '__main__':
    spec_json = sys.argv[1]
    print('I was here.')

    shutil.copyfile(FULL_KB_PATH, FULL_KB_BAK_PATH)

    run_combinations(spec_json)

    shutil.copyfile(FULL_KB_BAK_PATH, FULL_KB_PATH)

