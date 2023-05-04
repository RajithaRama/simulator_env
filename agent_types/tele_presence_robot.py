import random

from agent_types.home_agent import HomeAgent
from ethical_governor.ethical_governor import EthicalGovernor

import numpy as np

SELF_CHARGING = True
VISIBLE_DIST = 3


class Robot(HomeAgent):
    def __init__(self, unique_id, name, model, caller_name, governor_conf, start_battery):
        super().__init__(unique_id, name, model, "robot")
        self.buffered_instructions = []
        self.battery = start_battery
        self.time = 0
        self.ethical_governor = EthicalGovernor(governor_conf)
        self.roles = {caller_name: 'caller'}
        self.instruction_func_map = { "go_forward": self.move_forward, "go_backward": self.move_backward, "go_left": self.move_left, "go_right": self.move_right}


    def step(self):
        self.visible_dist = 3 if self.model.time_of_day == 'day' else 1

        if self.pos in self.model.things['charge_station']:

            if self.battery/100 < 1:
                self.battery += 3 if (100 - self.battery) >= 3 else (100 - self.battery)
        else:
            self.battery -= 0.2
        print("battery_lvl: " + str(self.battery))
        env = self.get_env_data()
        # self.follow(env)
        self.next_action(env)
        self.time += 1


    def next_action(self, env):

        buffered_instructions = env['stakeholders']['robot']['instruction_list']

        possible_actions = []

        # get and apply buffered_instructions
        if len(buffered_instructions):
            for instruction in buffered_instructions:
                possible_actions.append(self.instruction_func_map[instruction])
            possible_actions.append(self.decline_instruction)
        else:
            possible_actions.append(self.stay)

        self.make_final_decision(possible_actions, env)

    def make_final_decision(self, possible_actions, env):

        env['suggested_actions'] = possible_actions

        recommendations = self.ethical_governor.make_recommendations(env)
        print('Action recommended at step ' + str(self.time) + ': ' + str(recommendations))

        if len(recommendations) == 1:
            recommendations[0][0](*recommendations[0][1:])
            print('Action executed: ' + str(recommendations[0][0]))
            return
        else:
            #TODO: implement a way to choose between multiple recommendations
            pass

    def is_possible_move(self, move):
        return move in self.mode.get_moveable_area()

    def move(self, pos):
        self.model.grid.move_agent(self, pos)

    def move_forward(self):
        next_pos = (self.pos[0], self.pos[1] + 1)
        if self.is_possible_move(next_pos):
            self.move(next_pos)
        else:
            self.decline_instruction("move_forward", "I can't move forward from the current position", "caller")
            self.stay()

    def move_backward(self):
        next_pos = (self.pos[0], self.pos[1] - 1)
        if self.is_possible_move(next_pos):
            self.move(next_pos)
        else:
            self.decline_instruction("move_backward", "I can't move backward from the current position", "caller")
            self.stay()
    def move_right(self):
        next_pos = (self.pos[0] + 1, self.pos[1])
        if self.is_possible_move(next_pos):
            self.move(next_pos)
        else:
            self.decline_instruction("move_right", "I can't move right from the current position", "caller")
            self.stay()

    def move_left(self):
        next_pos = (self.pos[0] - 1, self.pos[1])
        if self.is_possible_move(next_pos):
            self.move(next_pos)
        else:
            self.decline_instruction("move_left", "I can't move left from the current position", "caller")
            self.stay()

    def stay(self):
        pass

    def decline_instruction(self, instruction, reason, caller_name):
        # TODO: implement a way to decline instructions
        pass
        
    

