import mesa

from mesa_exp_1 import Home


def robot_portrayal(agent):
    portrayal = {
        "Filled": "true",
        "Layer": 0,
        "r": 0.5,
    }

    if agent.type == 'robot':
        portrayal["Color"] = "red"
        portrayal["Shape"] = "square"
    elif agent.type == 'patient':
        portrayal["Color"] = "blue"
        portrayal["Shape"] = "circle"

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

grid = mesa.visualization.CanvasGrid()