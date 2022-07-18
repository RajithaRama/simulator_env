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

server = ModularVisualization.ModularServer(
    Home,
    [grid],
    "Home model", {}
)

server.port = 8123

server.launch()