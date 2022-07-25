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


# def patient_portrayal(agent):
#     portrayal = {
#         "Shape": "circle",
#         "Color": "blue",
#         "Filled": "true",
#         "Layer": 0,
#         "r": 0.5,
#     }
#     return portrayal

grid = modules.CanvasGrid(agent_portrayal, 13, 13, 494, 494)



# Patient 1 path
# start
patient_1_path = [(6, 5)]

# Move to couch in common area
patient_1_path.extend([(7, 5), (7, 4), (7, 3), (8, 3), (8, 2)])

# wait in couch for 60 secs
for i in range(5):
    patient_1_path.append((8, 2))

# move to Kitchen
patient_1_path.extend([(8, 2), (8, 3), (7, 3), (7, 4), (7, 5), (6, 5), (5, 5), (5, 4), (5, 3), (4, 3), (3, 3), (2, 3),
                       (2, 2)])

# wait in kitchen chair for 15 secs
for i in range(15):
    patient_1_path.append((2, 2))


#Patient 2 path

patient_2_path = []
for i in range(94):
    patient_2_path.append((9, 2))

server = ModularVisualization.ModularServer(
    Home,
    [grid],
    "Home model", {"no_patients": 2, "patient_starts": [patient_1_path[0], patient_2_path[0]], "robot_start": (5, 5), "patient_paths": [patient_1_path, patient_2_path]}
)

server.port = 8123

server.launch()