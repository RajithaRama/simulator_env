from mesa_updated.visualization import ModularVisualization, modules

from Models.home import Home


def agent_portrayal(agent):
    portrayal = {
        "Filled": "true",
        "Layer": 1,
    }
    # portrayal["Color"] = "red"
    # portrayal["Shape"] = "circle"
    if agent.type == 'robot':
        portrayal["Color"] = "red"
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
    elif agent.type == 'patient':
        portrayal["Color"] = "blue"
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
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

# move to Kitchen
patient_1_path.extend(
    [((5, 5), ''), ((5, 4), ''), ((5, 3), ''), ((4, 3), ''), ((3, 3), ''), ((2, 3), ''), ((2, 2), '')])

# wait in kitchen chair for 30 steps
for i in range(30):
    patient_1_path.append(((2, 2), ''))

# Path to bathroom (with command 'do_not_follow_to__bathroom')
patient_1_path.extend([((2, 3), ''), ((3, 3), ''), ((4, 3), ''), ((5, 3), ''), ((5, 4), ''), ((5, 5), ''), ((5, 6), ''),
                       ((5, 7), ''), ((5, 8), ''), ((6, 8), ''), ((7, 8), ''), ((8, 8), ''),
                       ((9, 8), 'do_not_follow_to__bathroom'), ((10, 8), ''),
                       ((10, 9), '')])

# Wait in Bathroom for 20 steps
for i in range(20):
    patient_1_path.append(((10, 10), ''))

# Path to kitchen (with command 'continue')
patient_1_path.extend([((10, 9), ''), ((10, 8), ''), ((9, 8), ''), ((8, 8), 'continue'), ((7, 8), ''), ((6, 8), ''),
                       ((5, 8), ''), ((5, 7), ''), ((5, 6), ''), ((5, 5), ''), ((5, 4), ''), ((5, 3), ''), ((4, 3), ''),
                       ((3, 3), ''), ((2, 3), ''), ((2, 2), '')])

grid = modules.CanvasGrid(agent_portrayal, 13, 13, 494, 494)

server = ModularVisualization.ModularServer(
    Home,
    [grid],
    "Home model", {"no_patients": 1, "patient_starts": [patient_1_path[0][0]], "robot_start": (5, 5),
                   "patient_paths": [patient_1_path], "governor_conf": 'experiments/bathroom_dilemma_deontology'
                                                                       '/elder_care_sim_deontology.yaml'}
)

server.port = 8123

server.launch()
