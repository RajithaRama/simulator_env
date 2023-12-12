from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
print(sys.path)

from mesa_updated.visualization import ModularVisualization, modules


from Models.home_telepresence import Home
from agent_types.caller import CALLER_TYPE
from agent_types.tele_presence_robot import Autonomy, Control_Bias, Wellbeing_Pref

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
    elif agent.type == 'care_worker':
        portrayal["Shape"] = "careworker.png"
        # portrayal["Color"] = "blue"
    elif agent.type == 'wall':
        portrayal["Color"] = "black"
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["xAlign"] = 0.5
        portrayal["yAlign"] = 0.5
    return portrayal

"""
Case 5: character bias towards caller. 
Receiver is okay to be seen, but care worker is not. Both in the receiver's room.
No other residents.
caller = Doctor
"""

# Patient 1 path
# start
patient_1_path = [((8, 11), '')]
care_worker_path = [((7, 11), '')]


caller_instructions = ['call', 'go_forward', 'go_forward', 'go_forward', 'go_forward', 'go_right', 'go_right']

patient_1_preference = {
    'bedroom': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    'bedroom_close_bed': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        }, 
    'kitchen': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    'bathroom': {
        'receiver': {
            'with_company': False, 
            'alone': False
            }, 
        '3rd_party': {
            'with_company': False, 
            'alone': False
            }
        }, 
    'living': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    }

care_worker_preference = {
    'bedroom': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': False, 
            'alone': False
            }
        }, 
    'bedroom_close_bed': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': False, 
            'alone': False
            }
        },
    'kitchen': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    'bathroom': {
        'receiver': {
            'with_company': False, 
            'alone': False
            }, 
        '3rd_party': {
            'with_company': False, 
            'alone': False
            }
        }, 
    'living': {
        'receiver': {
            'with_company': True, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': True, 
            'alone': True
            }
        },
    'other': {
        'receiver': {
            'with_company': False, 
            'alone': True
            }, 
        '3rd_party': {
            'with_company': False, 
            'alone': True
            }
        },
    }

caller_data = {
    'commands': caller_instructions,
    'type': CALLER_TYPE.DOCTOR,
    'calling_resident': 'patient_0'
}

character = {
    'control_bias': {
        'caller': Control_Bias.HIGH,
        'receiver': Control_Bias.LOW,
        'other': Control_Bias.NONE,
        'worker': Control_Bias.HIGH
    },
    'autonomy': Autonomy.HIGH,
    'wellbeing_value_preference': Wellbeing_Pref.LOW
}

worker_data = {
    'path': care_worker_path,
    'preferences': care_worker_preference
}

grid = modules.CanvasGrid(agent_portrayal, 13, 13, 494, 494)
conversations = modules.ConversationBox()

server = ModularVisualization.ModularServer(
    Home,
    [grid, conversations],
    "Home model", {"no_patients": 1, "patient_starts": [patient_1_path[0][0]], "robot_start": (5, 5),
                   "patient_paths": [patient_1_path], "caller_data": caller_data, "patient_preferences": [patient_1_preference], "robot_character": character,
                   "worker_data": worker_data, "governor_conf": 'experiments/tele_presence_dilemma_PSRB/elder_care_sim_PSRB.yaml', "time_of_day": "day"}
)

server.port = 8123

server.launch()
