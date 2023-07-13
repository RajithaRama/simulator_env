import random

from agent_types.home_agent import HomeAgent
from ethical_governor.ethical_governor import EthicalGovernor

import numpy as np

SELF_CHARGING = True
VISIBLE_DIST = 3


class Robot(HomeAgent):
    def __init__(self, unique_id, name, model, caller_name, governor_conf, start_battery, patient_preferences):
        super().__init__(unique_id, name, model, "robot")
        self.buffered_instructions = []
        self.battery = start_battery
        self.time = 0
        self.ethical_governor = EthicalGovernor(governor_conf)
        self.instruction_func_map = { 
            "go_forward": self.move_forward, 
            "go_backward": self.move_backward, 
            "go_left": self.move_left, 
            "go_right": self.move_right, 
            "call": self.take_call,
            # "hung_up": self.hung_up
            }
        self.on_call = False
        self.caller = None
        self.patient_preferences = patient_preferences


    def step(self):
        self.visible_dist = VISIBLE_DIST if self.model.time_of_day == 'day' else 1

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
        if buffered_instructions:
            for instruction in buffered_instructions:
                action = self.instruction_func_map[instruction[0]]
                
                if action == self.take_call:
                    possible_actions.append((action, instruction[1].id))
                    possible_actions.append((self.decline_call, instruction[1].id))
                else:
                    possible_actions.append((action, ))
                    possible_actions.append((self.decline_instruction_end_call, instruction[0], "caller"))
                    
        else:
            possible_actions.append((self.stay, ))
            possible_actions.append((self.decline_call, self.caller))

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
            
            user_commands = {value for key, value in self.instruction_func_map.items()}
            for recommendation in recommendations:
                if recommendation[0] in user_commands:
                    recommendations[0][0](*recommendations[0][1:])
                    print('Action executed: ' + str(recommendation[0]))
                    return

            # if no user command is found, execute the first recommendation
            recommendations[0][0](*recommendations[0][1:])
            return

    def is_possible_move(self, move):
        return move in self.model.get_moveable_area(self.pos)

    def move(self, pos):
        self.model.grid.move_agent(self, pos)

    def move_forward(self, act=True):
        next_pos = (self.pos[0], self.pos[1] + 1)
        
        if self.on_call and self.is_possible_move(next_pos):
            if act:
                self.move(next_pos)
            else:
                return next_pos
        elif not self.on_call:
            raise Exception("Robot is not on call")
        else:
            if not act:
                return self.pos
            self.decline_instruction("Robot can't move forward from the current position", "caller")
            self.stay()

    def move_backward(self, act=True):
        next_pos = (self.pos[0], self.pos[1] - 1)
        if self.on_call and self.is_possible_move(next_pos):
            if act:
                self.move(next_pos)
            else:
                return next_pos
        elif not self.on_call:
            raise Exception("Robot is not on call")
        else:
            if not act:
                return self.pos
            self.decline_instruction("Robot can't move backward from the current position", "caller")
            self.stay()
    def move_right(self, act=True):
        next_pos = (self.pos[0] + 1, self.pos[1])
        if self.on_call and self.is_possible_move(next_pos):
            if act:
                self.move(next_pos)
            else:
                return next_pos
        elif not self.on_call:
            raise Exception("Robot is not on call")
        else:
            if not act:
                return self.pos
            self.decline_instruction("Robot can't move right from the current position", "caller")
            self.stay()

    def move_left(self, act=True):
        next_pos = (self.pos[0] - 1, self.pos[1])
        if self.on_call and self.is_possible_move(next_pos):
            if act:
                self.move(next_pos)
            else:
                return next_pos
        elif not self.on_call:
            raise Exception("Robot is not on call")
        else:
            if not act:
                return self.pos
            self.decline_instruction("Robot can't move left from the current position", "caller")
            self.stay()

    def take_call(self, caller_name):
        self.on_call = True
        self.caller = caller_name
        print("Robot: Answered the call from " + caller_name)

    def decline_call(self):
        code = -2
        msg = "Cannot answer the call now. Please try again later."
        reciever = self.model.get_stakeholder(self.caller)
        self.model.pass_message((msg, code), self, reciever)
        print("Robot: Declined the call from " + str(self.caller))
        
        # reset the robot state to default
        self.on_call = False
        self.caller = None

    def hung_up(self):
        self.on_call = False
        self.caller = None

    def stay(self, act=True):
        if not act:
            return self.pos

    def decline_instruction(self, reason, caller_name):
        code = -1
        msg = reason
        reciever = self.model.get_stakeholder(caller_name)
        self.model.pass_message((msg, code), self, reciever)
        print("Robot: Declined " + caller_name + " command. Reason: " + reason)

    def decline_instruction_end_call(self, instruction, caller_name):
        code = -2
        msg = "Declining the calller instruction " + instruction + " considering recommendations of the ethical governor. Call will be ending now. Please call at a later time."
        reciever = self.model.get_stakeholder(caller_name)
        self.model.pass_message((msg, code), self, reciever)

        self.on_call = False
        print("Robot: Declined " + caller_name + " command and ended the call.")

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
            agent_data['preferences'] = agent.preferences
            stakeholders[agent.id] = agent_data

        instructions = self.model.get_message(self)

        if instructions:
            for instruction in instructions:
                if instruction[0] in self.instruction_func_map.keys():
                    caller = {}
                    caller['id'] = instruction[1].id
                    caller['type'] = instruction[1].type
                    caller['calling_resident'] = instruction[1].calling_resident

                    stakeholders['caller'] = caller

        elif self.on_call:
            caller = {}
            caller['id'] = self.caller
            caller['type'] = self.model.get_stakeholder(self.caller).type
            caller['calling_resident'] = self.model.get_stakeholder(self.caller).calling_resident

            stakeholders['caller'] = caller

        robot_data = {'id': self.id, 'type': "robot", 'pos': self.pos, 'location': self.model.get_location(self.pos),
                      'battery_level': self.battery, 'model': self, 'on_call': self.on_call,
                      'visible_dist': self.visible_dist, 'instruction_list': instructions}

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
