import shutil
import subprocess
import sys
import os

python_interpreter_path = "C:\\Users\\rajit\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\simulator-env-qWiytRf7-py3.11\\Scripts\\python.exe"
cases = []
expertiment_dir = "C:\\Users\\rajit\\PycharmProjects\\simulator_env\\experiments_cmd"
data_dir = "C:\\Users\\rajit\\PycharmProjects\\simulator_env\\data"

def run_case(dir, case_name, output_name):
    # Run a case
    # case_name: name of the simulating case
    subprocess.run([python_interpreter_path, os.path.join(expertiment_dir, dir, case_name + '.py')], check=True)

    # subprocess.run(['mkdir', '-p', os.path.join(data_dir, case_name)], check=True)
    if not os.path.exists(os.path.join(data_dir, output_name)):
        os.makedirs(os.path.join(data_dir, output_name))


    shutil.move('action_sequence.json', os.path.join(data_dir, output_name))
    shutil.move('utility_sequence.json', os.path.join(data_dir, output_name))
    # subprocess.run(['cp', 'action_sequence.json', os.path.join(data_dir, case_name)], check=True)
    # subprocess.run(['cp', 'utility_sequence.json', os.path.join(data_dir, case_name)], check=True)

if __name__ == "__main__":
    # getting command line arguments
    dir_name = sys.argv[1]
    output_name = sys.argv[2]
    case_names = sys.argv[3:]
    print(case_names)

    for case_name in case_names:
        run_case(dir=dir_name, case_name=case_name, output_name=output_name)
