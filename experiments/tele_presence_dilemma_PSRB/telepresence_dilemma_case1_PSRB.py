from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
print(sys.path)


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

caller_instructions = ['call','go_forward', 'go_right', 'go_right', 'go_backward', 'go_backward', 'go_right']

patient_1_preference = {
    'bedroom': {
        'reciever': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        }, 
    'kitchen': {
        'reciever': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    'bathroom': {
        'reciever': {
            'with_company': False, 
            'alone': False
            }, 
        '3rd_party': {
            'with_company': False, 
            'alone': False
            }
        }, 
    'living_room': {
        'reciever': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    }

patient_2_preference = {
    'bedroom': {
        'reciever': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        }, 
    'kitchen': {
        'reciever': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    'bathroom': {
        'reciever': {
            'with_company': False, 
            'alone': False
            }, 
        '3rd_party': {
            'with_company': False, 
            'alone': False
            }
        }, 
    'living_room': {
        'reciever': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    }

caller_data = {
    'commands': caller_instructions,
    'type': CALLER_TYPE.FAMILY,
    'calling_resident': 'patient_0'
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
