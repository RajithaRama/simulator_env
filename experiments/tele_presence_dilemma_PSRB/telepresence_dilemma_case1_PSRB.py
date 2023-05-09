from mesa_updated.visualization import ModularVisualization, modules


from Models.home_telepresence import Home
from agent_types.caller import CALLER_TYPE

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
patient_1_path = [((8, 2), '')]
patient_2_path = [((10, 2), '')]

caller_instructions = ['go_forward', 'go_left', 'go_left', 'go_backward', 'go_backward']

patient_1_preference = {}
patient_2_preference = {}

caller_data = {
    'commands': caller_instructions,
    'type': CALLER_TYPE.FAMILY
}


grid = modules.CanvasGrid(agent_portrayal, 13, 13, 494, 494)

server = ModularVisualization.ModularServer(
    Home,
    [grid],
    "Home model", {"no_patients": 2, "patient_starts": [patient_1_path[0][0], patient_2_path[0][0]], "robot_start": (5, 5),
                   "patient_paths": [patient_1_path, patient_2_path], "caller_data": caller_data, "patient_preferences": [patient_1_preference, patient_2_preference], "governor_conf":
                       'experiments/tele_presence_dilemma_PSRB/elder_care_sim_PSRB.yaml', "time_of_day": "day"}
)

server.port = 8123

server.launch()
