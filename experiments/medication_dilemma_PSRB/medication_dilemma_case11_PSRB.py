from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
print(sys.path)



from mesa_updated.visualization import ModularVisualization, modules


from Models.home_medication import Home, MedImpact

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
patient_1_path = [((2, 2), '')]


med_info = {"med_a": {"type": "painkiller", "impact": MedImpact.LOW}, "med_b": {"type": "supplement", "impact": MedImpact.MEDIUM}, "med_c": {"type": "Insulin", "impact": MedImpact.HIGH}}
patient_1_medication_preference = {"is_taking_meds": False, "responses": ["SNOOZE", "ACKNOWLEDGE"]}
timer_data = [[2, 30, 'med_b', 'patient_0', 0]]
character = {'wellbeing': 9, 'autonomy': 1, 'risk_propensity': 9}


grid = modules.CanvasGrid(agent_portrayal, 13, 13, 494, 494)
conversations = modules.ConversationBox()

server = ModularVisualization.ModularServer(
    Home,
    [grid, conversations],
    "Home model", {"no_patients": 1, "patient_starts": [patient_1_path[0][0]], "robot_start": (2, 1), "patient_healths": [0], "med_info": med_info,
                   "patient_paths": [patient_1_path], "patient_preferences": [patient_1_medication_preference], "governor_conf":
                       'experiments/medication_dilemma_PSRB/elder_care_sim_PSRB.yaml', "robot_character": character, "time_of_day": "day", "timer_data": timer_data}
)

server.port = 8123

server.launch()
