import os
import json


def get_cumilative_utilities(actions_sequence, utility_sequence):
    cumilative_utilities = {"follower_wellbeing": 0, "follower_autonomy": 0}
    for action, utilities in zip(actions_sequence, utility_sequence):
        for util, value in utilities[action].items():
            if util in cumilative_utilities:
                cumilative_utilities[util] += value
    return cumilative_utilities


action_sequence = json.load(open(os.path.join("ideal_behaviour", "bathroom_case4_autonomy", "action_sequence.json"), 'r'))
utility_sequence = json.load(open(os.path.join("ideal_behaviour", "bathroom_case4_autonomy", "utility_sequence.json"), 'r'))

# print(action_sequence)
# print(utility_sequence)

print(get_cumilative_utilities(action_sequence, utility_sequence))

action_sequence = json.load(open(os.path.join("ideal_behaviour", "bathroom_case4_wellbeing", "action_sequence.json"), 'r'))
utility_sequence = json.load(open(os.path.join("ideal_behaviour", "bathroom_case4_wellbeing", "utility_sequence.json"), 'r'))

# print(action_sequence)
# print(utility_sequence)

print(get_cumilative_utilities(action_sequence, utility_sequence))