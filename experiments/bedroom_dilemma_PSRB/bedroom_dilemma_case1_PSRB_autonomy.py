from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
print(sys.path)

from mesa_updated.visualization import ModularVisualization, modules

from Models.home import Home

# The patient go to the bathroom and stay 20 steps (average time)

def agent_portrayal(agent):
    portrayal = {
        "Filled": "true",
        "Layer": 1,
    }
    # portrayal["Color"] = "red"
    # portrayal["Shape"] = "circle"
    if agent.type == 'robot':
        # portrayal["Color"] = "red"
        portrayal["Shape"] = "robot.png"
        # portrayal["r"] = 0.5
    elif agent.type == 'patient':
        # portrayal["Color"] = "blue"
        portrayal["Shape"] = "elder.png"
        # portrayal["r"] = 0.5
    elif agent.type == 'wall':
        portrayal["Color"] = "black"
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["xAlign"] = 0.5
        portrayal["yAlign"] = 0.5
    return portrayal


# Patient 1 path
# start
patient_1_path = [((6, 5), '')]

# Path to bed (with command 'do_not_follow_to__bathroom')
patient_1_path.extend([((5, 5), ''), ((5, 6), ''),
                       ((5, 7), ''), ((5, 8), ''), ((5, 9), ''), ((5, 10), ''), ((5, 11), ''), ((6, 11), ''),
                       ((7, 11), 'do_not_follow_to__bedroom_close_bed'), ((8, 11), 'turn_off_lights')])


robot_character = {'wellbeing': 3, 'autonomy': 9, 'availability': 3}

grid = modules.CanvasGrid(agent_portrayal, 13, 13, 494, 494)

server = ModularVisualization.ModularServer(
    Home,
    [grid],
    "Home model", {"no_patients": 1, "patient_starts": [patient_1_path[0][0]], "robot_start": (5, 5),
                   "patient_paths": [patient_1_path], "patient_healths": [1], "patient_histories": [0], "governor_conf":
                       'experiments/bathroom_dilemma_PSRB/elder_care_sim_PSRB.yaml', "robo_battery": 100, "time_of_day": "day", "robot_character": robot_character}
)

server.port = 8123

server.launch()
