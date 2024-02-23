import itertools
import os
import shutil
import time
import json

from pathlib import Path
import sys
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

import genralisability_exp_scripts.modify_case_base_teleP as modify_case_base
import genralisability_exp_scripts.test_run_telepresence as test_run
import genralisability_exp_scripts.KvsP_exp_run_script_teleP as KvsP_exp_run_script_teleP

FULL_KB_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_telepresence.json'
FULL_KB_BAK_PATH = 'ethical_governor/blackboard/commonutils/cbr/case_base_gen_telepresence_temp_bak.json'

# k = [2, 3, 5, 8]
# percentages = [0.1, 0.25, 0.5, 0.8, 1]
# percentages = [1]
# scenarios = ['Bathroom_Scn1', 'Bathroom_Scn3', 'Bathroom_Scn4', 'Bathroom_Scn5', 'Bathroom_Scn6', 'Bedroom_Scn1',
#              'Bedroom_Scn2', 'Bedroom_Scn3']

data_dir = "Data"



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



# for k_value in k:
#     for percentage in percentages:
# for i in range(len(scenarios)):
#     for comb in itertools.combinations(scenarios, i + 1):
#         print(comb)
#         n += 1

# print(n) # 5100 combinations if ran all


scenario_casename_map = {'bed_case1': ['telepresence_dilemma_bedroom_case1_PSRB_an.py', 'telepresence_dilemma_bedroom_case1_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_bedroom_case1_PSRB_ro_ah_wl.py', 'telepresence_dilemma_bedroom_case1_PSRB_row_ah_wl.py',
                                       'telepresence_dilemma_bedroom_case1_PSRB_row_al_wl.py', 'telepresence_dilemma_bedroom_case1_PSRB_w_ah_wh.py'],
                         'bed_case2': ['telepresence_dilemma_bedroom_case2_PSRB_an.py', 'telepresence_dilemma_bedroom_case2_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_bedroom_case2_PSRB_ro_ah_wl.py', 'telepresence_dilemma_bedroom_case2_PSRB_row_ah_wl.py',
                                       'telepresence_dilemma_bedroom_case2_PSRB_row_al_wl.py', 'telepresence_dilemma_bedroom_case2_PSRB_w_ah_wh.py'],
                         'bed_case3': ['telepresence_dilemma_bedroom_case3_PSRB_an.py', 'telepresence_dilemma_bedroom_case3_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_bedroom_case3_PSRB_ro_ah_wl.py', 'telepresence_dilemma_bedroom_case3_PSRB_row_ah_wl.py',
                                       'telepresence_dilemma_bedroom_case3_PSRB_row_al_wl.py', 'telepresence_dilemma_bedroom_case3_PSRB_w_ah_wh.py'],
                         'bed_case4': ['telepresence_dilemma_bedroom_case4_PSRB_an.py', 'telepresence_dilemma_bedroom_case4_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_bedroom_case4_PSRB_ro_ah_wl.py', 'telepresence_dilemma_bedroom_case4_PSRB_row_ah_wl.py',
                                       'telepresence_dilemma_bedroom_case4_PSRB_row_al_wl.py', 'telepresence_dilemma_bedroom_case4_PSRB_w_ah_wh.py'],
                        'bed_case5': ['telepresence_dilemma_bedroom_case5_PSRB_an.py', 'telepresence_dilemma_bedroom_case5_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_bedroom_case5_PSRB_ro_ah_wl.py', 'telepresence_dilemma_bedroom_case5_PSRB_row_ah_wl.py',
                                       'telepresence_dilemma_bedroom_case5_PSRB_row_al_wl.py', 'telepresence_dilemma_bedroom_case5_PSRB_w_ah_wh.py'],
                        'bed_case6': ['telepresence_dilemma_bedroom_case6_PSRB_an.py', 'telepresence_dilemma_bedroom_case6_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_bedroom_case6_PSRB_ro_ah_wl.py', 'telepresence_dilemma_bedroom_case6_PSRB_row_ah_wl.py',
                                       'telepresence_dilemma_bedroom_case6_PSRB_row_al_wl.py', 'telepresence_dilemma_bedroom_case6_PSRB_w_ah_wh.py'],
                        'bed_case0': ['telepresence_dilemma_bedroom_everyday_PSRB_an.py', 'telepresence_dilemma_bedroom_everyday_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_bedroom_everyday_PSRB_ro_ah_wl.py', 'telepresence_dilemma_bedroom_everyday_PSRB_row_ah_wl.py',
                                       'telepresence_dilemma_bedroom_everyday_PSRB_row_al_wl.py', 'telepresence_dilemma_bedroom_everyday_PSRB_w_ah_wh.py'],
                        'living_case1': ['telepresence_dilemma_livingroom_case1_PSRB_an.py', 'telepresence_dilemma_livingroom_case1_PSRB_cw_al_wh.py',
                                        'telepresence_dilemma_livingroom_case1_PSRB_row_ah_wl.py', 'telepresence_dilemma_livingroom_case1_PSRB_row_al_wl.py',
                                       'telepresence_dilemma_livingroom_case1_PSRB_rw_ah_wl.py', 'telepresence_dilemma_livingroom_case1_PSRB_w_ah_wh.py'],
                        'living_case2': ['telepresence_dilemma_livingroom_case2_PSRB_an.py', 'telepresence_dilemma_livingroom_case2_PSRB_cw_al_wh.py',
                                            'telepresence_dilemma_livingroom_case2_PSRB_row_ah_wl.py', 'telepresence_dilemma_livingroom_case2_PSRB_row_al_wl.py',
                                             'telepresence_dilemma_livingroom_case2_PSRB_rw_ah_wl.py', 'telepresence_dilemma_livingroom_case2_PSRB_w_ah_wh.py'],
                        'living_case3': ['telepresence_dilemma_livingroom_case3_PSRB_an.py', 'telepresence_dilemma_livingroom_case3_PSRB_cw_al_wh.py',
                                            'telepresence_dilemma_livingroom_case3_PSRB_row_ah_wl.py', 'telepresence_dilemma_livingroom_case3_PSRB_row_al_wl.py',
                                             'telepresence_dilemma_livingroom_case3_PSRB_rw_ah_wl.py', 'telepresence_dilemma_livingroom_case3_PSRB_w_ah_wh.py'],
                        'living_case4': ['telepresence_dilemma_livingroom_case4_PSRB_an.py', 'telepresence_dilemma_livingroom_case4_PSRB_cw_al_wh.py',
                                            'telepresence_dilemma_livingroom_case4_PSRB_row_ah_wl.py', 'telepresence_dilemma_livingroom_case4_PSRB_row_al_wl.py',
                                             'telepresence_dilemma_livingroom_case4_PSRB_rw_ah_wl.py', 'telepresence_dilemma_livingroom_case4_PSRB_w_ah_wh.py'],
                        'living_case5': ['telepresence_dilemma_livingroom_case5_PSRB_an.py', 'telepresence_dilemma_livingroom_case5_PSRB_cw_al_wh.py',
                                            'telepresence_dilemma_livingroom_case5_PSRB_row_ah_wl.py', 'telepresence_dilemma_livingroom_case5_PSRB_row_al_wl.py',
                                             'telepresence_dilemma_livingroom_case5_PSRB_rw_ah_wl.py', 'telepresence_dilemma_livingroom_case5_PSRB_w_ah_wh.py'],
                        'living_case6': ['telepresence_dilemma_livingroom_case6_PSRB_an.py', 'telepresence_dilemma_livingroom_case6_PSRB_cw_al_wh.py',
                                            'telepresence_dilemma_livingroom_case6_PSRB_row_ah_wl.py', 'telepresence_dilemma_livingroom_case6_PSRB_row_al_wl.py',
                                             'telepresence_dilemma_livingroom_case6_PSRB_rw_ah_wl.py', 'telepresence_dilemma_livingroom_case6_PSRB_w_ah_wh.py'],
                        'living_case0': ['telepresence_dilemma_livingroom_everyday_PSRB_an.py', 'telepresence_dilemma_livingroom_everyday_PSRB_cw_al_wh.py',
                                            'telepresence_dilemma_livingroom_everyday_PSRB_row_ah_wl.py', 'telepresence_dilemma_livingroom_everyday_PSRB_row_al_wl.py',
                                             'telepresence_dilemma_livingroom_everyday_PSRB_rw_ah_wl.py', 'telepresence_dilemma_livingroom_everyday_PSRB_w_ah_wh.py']
                        }


scnario_dir_name_ids_map = {'bed_case1': 'Bed1', 'bed_case2': 'Bed2', 'bed_case3': 'Bed3', 'bed_case4': 'Bed4', 'bed_case5': 'Bed5', 'bed_case6': 'Bed6',
                            'bed_case0': 'Bed0', 'living_case1': 'Living1', 'living_case2': 'Living2', 'living_case3': 'Living3', 'living_case4': 'Living4',
                            'living_case5': 'Living5', 'living_case6': 'Living6', 'living_case0': 'Living0'}

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
            # if len(comb) == 1 and ('Scn0' in comb):
            #     continue
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

        KvsP_exp_run_script_teleP.run_experiment(spec_json_path, file_list)
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
    directory = os.path.join(data_dir, experiment)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    print(directory)
    print(os.path.join(directory, spec_name + '_spec.json'))
    with open(os.path.join(directory, spec_name + '_spec.json'), 'w') as f:
        json.dump(KvP_spec, f)

    return os.path.join(directory, spec_name + '_spec.json')


if __name__ == '__main__':
    spec_json = sys.argv[1]
    print('I was here.')

    shutil.copyfile(FULL_KB_PATH, FULL_KB_BAK_PATH)

    run_combinations(spec_json)

    shutil.copyfile(FULL_KB_BAK_PATH, FULL_KB_PATH)
