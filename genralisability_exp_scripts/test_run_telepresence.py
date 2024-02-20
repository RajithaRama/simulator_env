import json
import shutil
import subprocess
import sys
import os
import time

python_interpreter_path = "C:\\Users\\rajit\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\simulator-env-qWiytRf7-py3.11\\Scripts\\python.exe"
cases = []
expertiment_dir = "experiments_cmd"
data_dir = "Data"


def run_case(dir, case_name, experiment, condition, output_name=None):


    if output_name is None:
        output_name = case_name.replace('.py', '')

    case_run_start = time.time()
    # Run a case
    # case_name: name of the simulating case
    subprocess.run([python_interpreter_path, os.path.join(dir, case_name)], check=True)
    case_run_end = time.time()
    case_run_time = case_run_end - case_run_start


    # subprocess.run(['mkdir', '-p', os.path.join(data_dir, case_name)], check=True)
    if not os.path.exists(os.path.join(data_dir, experiment, condition, output_name)):
        os.makedirs(os.path.join(data_dir, experiment, condition, output_name))

    shutil.copy('action_sequence.json', os.path.join(data_dir, experiment, condition, output_name))
    shutil.copy('utility_sequence.json', os.path.join(data_dir, experiment, condition, output_name))
    shutil.copy('human_action_sequence.json', os.path.join(data_dir, experiment, condition, output_name))

    if 'telepresence_dilemma_PSRB' in dir:
        shutil.copy('PSRB_telepresence_dilemma.log', os.path.join(data_dir, experiment, condition, output_name))
    # subprocess.run(['cp', 'action_sequence.json', os.path.join(data_dir, case_name)], check=True)
    # subprocess.run(['cp', 'utility_sequence.json', os.path.join(data_dir, case_name)], check=True)

    # dump run time info.
    json.dump({'case_run_time': case_run_time},
              open(os.path.join(data_dir, experiment, condition, output_name, 'case_run_time.json'), 'w'))


if __name__ == "__main__":
    # getting command line arguments
    # dir_name = sys.argv[1]
    # output_name = sys.argv[2]
    # case_names = sys.argv[3:]
    # print(case_names)
    #
    # for case_name in case_names:
    #     run_case(dir=dir_name, case_name=case_name, experiment='testing', condition='test', output_name=output_name)

    run_case(dir='experiments_cmd\\tele_presence_dilemma_PSRB\\teleP_dilemma', case_name='telepresence_dilemma_bedroom_case2_PSRB_an.py',
             experiment='testing', condition='test', output_name='telepresence_dilemma_PSRB')