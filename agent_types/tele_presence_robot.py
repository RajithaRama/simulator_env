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
                action = self.instruction_func_map[instruction[0]]
                possible_actions.append(action)
            possible_actions.append(self.decline_instruction)

        possible_actions.append(self.stay)

        self.make_final_decision(possible_actions, env)

    def make_final_decision(self, possible_actions, env):

        env['suggested_actions'] = possible_actions

        recommendations = self.ethical_governor.recommend(env)
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
            self.decline_instruction("I can't move left from the current position", "caller")
            self.stay()

    def stay(self):
        pass

    def decline_instruction(self, reason, caller_name):
        code = -1
        msg = reason
        reciever = self.model.get_stakeholder(caller_name)
        self.model.pass_message((msg, code), self, reciever)

    
    def get_env_data(self):
        env_data = {}
        visible_stakeholders = self.model.visible_stakeholders(self.pos, self.visible_dist)

        stakeholders = {}
        for agent in visible_stakeholders:
            # print(agent.type)
            agent_data = {}
            if agent.type == 'wall':
                continue

            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            # agent_data['seen_time'] = self.time
            # agent_data['seen_pos'] = agent.pos
            agent_data['seen_location'] = self.model.get_location(agent.pos)
            agent_data['pos'] = agent.pos
            agent_data['seen'] = True
            stakeholders[agent.id] = agent_data

        caller = {'id': 'caller', 'type': 'caller'}
        stakeholders['follower'] = caller

        robot_data = {'id': "this", 'type': "robot", 'pos': self.pos, 'location': self.model.get_location(self.pos),
                      'battery_level': self.battery, 'model': self,
                      'visible_dist': self.visible_dist, 'instruction_list': self.model.get_message(self)}

        stakeholders['robot'] = robot_data

        env_data['stakeholders'] = stakeholders
        # env['']

        environment = {"time_of_day": self.model.time_of_day, "time": self.time,
                       "walls": self.model.wall_coordinates,
                       "things": self.model.things,
                       "things_robot_inaccessible": self.model.things_robot_inaccessible
                       }
        env_data['environment'] = environment
        env_data['other_inputs'] = {}

        # print("robot env: " + str(env))
        return env_data
