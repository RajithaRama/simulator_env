import random

from agent_types.home_agent import HomeAgent
from ethical_governor.ethical_governor import EthicalGovernor

import numpy as np

SELF_CHARGING = True
VISIBLE_DIST = 3


class Robot(HomeAgent):
    def __init__(self, unique_id, name, model, follower_name, governor_conf, start_battery):
        super().__init__(unique_id, name, model, "robot")
        self.buffered_instructions = []
        self.battery = start_battery
        self.time = 0
        self.last_seen_location = None
        self.last_seen_pos = None
        self.last_seen_time = None
        self.follower_name = follower_name
        self.not_follow_request = False
        self.not_follow_locations = []
        self.ethical_governor = EthicalGovernor(governor_conf)

    def step(self):
        if self.pos in self.model.things['charge_station']:
            self.battery += 3
        else:
            self.battery -= 0.1
        # print("battery_lvl: " + str(self.battery))
        env = self.get_env_data()
        # self.follow(env)
        self.next_action(env)
        self.time += 1

    def next_action(self, env):

        buffered_instructions = env['stakeholders']['robot']['instruction_list']

        possible_actions = []

        # get and apply buffered_instructions
        if len(buffered_instructions):
            # If user istruct to make clear, robot try to move away from the said user
            for instruction in buffered_instructions:
                # instruction = (command, giver)
                # add make clear instruction to possible action list
                if 'move_away' == instruction[0]:
                    possible_actions.append((self.move_away, instruction[1]))
                if 'do_not_follow_to' in instruction[0]:
                    ins_split = instruction[0].split('__')
                    if ins_split[1] in self.model.locations.keys():
                        self.do_not_follow_to(to_location=ins_split[1], follower=instruction[1])
                        env['stakeholders']['robot']['not_follow_request'] = self.not_follow_request
                if 'continue' == instruction[0] and self.not_follow_request:
                    self.remove_do_not_follow()

        # get visible neighbours and set follower
        visible_neighbors = self.model.visible_stakeholders(self.pos, VISIBLE_DIST)

        self.follower = None
        for neighbor in visible_neighbors:
            if neighbor.id == self.follower_name:
                self.follower = neighbor
                self.last_seen_pos = self.follower.pos
                self.last_seen_location = self.model.get_location(self.follower.pos)
                old_last_seen_time = self.last_seen_time
                self.last_seen_time = self.time

        # Follow or go to last seen
        if self.follower:
            possible_actions.append((self.follow, self.follower))
        else:
            possible_actions.append((self.go_to_last_seen,))

        # staying the same place
        possible_actions.append((self.stay,))

        # if follower in a restricted area stay
        # if follower and (self.model.get_location(follower.pos) in self.not_follow_locations):
        #     possible_actions.append((self.stay,))
        # elif not follower and (self.model.get_location(self.last_seen_pos) in self.not_follow_locations):
        #     possible_actions.append((self.stay,))

        if SELF_CHARGING:
            possible_actions.append((self.go_to_charge_station,))

        self.make_final_decision(possible_actions, env)

    def make_final_decision(self, possible_actions, env):

        env['suggested_actions'] = possible_actions
        env['other_inputs'] = {'robot_model': self}

        recommendations = self.ethical_governor.recommend(env)
        print('Action executed at step ' + str(self.time) + ': ' + str(recommendations))

        if len(recommendations) == 1:
            recommendations[0][0](*recommendations[0][1:])
            print('Action executed: ' + str(recommendations[0][0]))
            return
        else:
            # Check for low battery
            if self.battery < 5 or (self.battery < 80 and (self.pos in self.model.things['charge_station'])):
                for action in recommendations:
                    if self.go_to_charge_station == action[0]:
                        action[0](*action[1:])
                        print('Action executed at step ' + str(self.time) + ': ' + str(action[0]))
                        return

            # Check for follow
            for action in recommendations:
                if self.follow == action[0]:
                    action[0](*action[1:])
                    print('Action executed at step ' + str(self.time) + ': ' + str(action[0]))
                    return
                # if self.move_away == action[0]:
                #     action[0](*action[1:])
                #     return
                # if self.not_follow_request and (self.stay == action[0]):
                #     action[0](*action[1:])
                #     return

            # Else select the move result closest to the follower
            dist = []
            for action in recommendations:
                next_pos = action[0](*action[1:], act=False)
                if env['stakeholders']['follower']['seen']:
                    dist.append(self.model.get_shortest_distance(current=next_pos,
                                                                 dest=env['stakeholders']['follower']['seen_pos'],
                                                                 ignore_agents=[self, self.follower]))
                else:
                    dist.append(self.model.get_shortest_distance(current=next_pos,
                                                                 dest=env['stakeholders']['follower']['last_seen_pos'],
                                                                 ignore_agents=[self]))
            min_dist = min(dist)
            indices = [i for i in range(len(dist)) if dist[i] == min_dist]
            if len(indices) == 1:
                action = recommendations[indices[0]]
            else:
                action = random.choice([recommendations[j] for j in indices])

            action[0](*action[1:])
            print('Action executed at step ' + str(self.time) + ': ' + str(action[0]))
            return

    def move_away(self, follower, act=True):
        """ pos - position to move away from"""
        possible_steps = self.model.get_moveable_area(self.pos, [self])

        distances = {}
        for step in possible_steps:
            distances[self.model.get_shortest_distance(step, follower.pos, [self, follower])] = step

        next_pos = distances[max(distances.keys())]

        if act:
            self.move(next_pos)
        else:
            return next_pos

    def stay(self, location=None, act=True):
        if location:
            next_pos = location
        else:
            next_pos = self.pos

        if act:
            self.move(next_pos)
        else:
            return next_pos

    def do_not_follow_to(self, to_location, follower):
        self.not_follow_request = True
        self.not_follow_locations.append(to_location)

    def remove_do_not_follow(self):
        self.not_follow_request = False
        self.not_follow_locations.pop()

    def follow(self, follower, act=True):
        possible_steps = self.model.get_moveable_area(self.pos, [self])

        distances = {}
        for step in possible_steps:
            distances[self.model.get_shortest_distance(step, follower.pos, [self, follower])] = step

        next_pos = distances[min(distances.keys())]

        if act:
            self.move(next_pos)
        else:
            return next_pos

    def go_to_pos(self, pos, ignore_agents=None, act=True):
        if pos == self.pos:
            return

        for thing in self.model.things_robot_inaccessible:
            if (pos in self.model.things[thing]) or not (self.model.grid.is_cell_empty(pos)):
                raise EnvironmentError("Robot cannot move onto " + thing)

        possible_steps = self.model.get_moveable_area(self.pos, ignore_agents)

        distances = {}
        for step in possible_steps:
            distances[self.model.get_shortest_distance(step, pos, ignore_agents)] = step

        next_pos = distances[min(distances.keys())]

        if act:
            self.move(next_pos)
        else:
            return next_pos

    def go_to_charge_station(self, act=True):
        if act:
            self.go_to_pos(self.model.things['charge_station'][0], [self], act=act)
        else:
            return self.go_to_pos(self.model.things['charge_station'][0], [self], act=act)

    def go_to_last_seen(self, act=True):
        possible_locations = [self.last_seen_pos]

        while len(possible_locations):
            possible_pos = None
            try:
                possible_pos = possible_locations.pop(0)
                next_pos = self.go_to_pos(possible_pos, [self], act=act)
            except EnvironmentError:
                possible_locations.extend(self.model.get_moveable_area(possible_pos))
                continue
            break

        if next_pos:
            return next_pos

    def move(self, pos):
        self.model.grid.move_agent(self, pos)

    def get_env_data(self):
        env_data = {}
        visible_stakeholders = self.model.visible_stakeholders(self.pos, VISIBLE_DIST)

        follower_in_data = False

        stakeholders = {}
        for agent in visible_stakeholders:
            # print(agent.type)
            agent_data = {}
            if agent.type == 'wall':
                continue

            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            agent_data['seen_time'] = self.time
            agent_data['seen_pos'] = agent.pos
            agent_data['seen_location'] = self.model.get_location(agent.pos)
            agent_data['pos'] = agent.pos
            agent_data['seen'] = True

            if agent.id == self.follower_name:
                follower_in_data = True
                agent_data['last_seen_time'] = self.last_seen_time
                agent_data['last_seen_pos'] = self.last_seen_pos
                agent_data['last_seen_location'] = self.model.get_location(
                    self.last_seen_pos) if self.last_seen_pos else None
                agent_data['follower'] = True
                stakeholders['follower'] = agent_data
            else:
                agent_data['follower'] = False
                stakeholders[agent.id] = agent_data

        if not follower_in_data:
            agent_data = {'id': self.follower_name, 'type': 'patient', 'last_seen_time': self.last_seen_time,
                          'follower':
                              True, 'last_seen_pos': self.last_seen_pos, 'last_seen_location': self.last_seen_location,
                          'seen': False}
            stakeholders['follower'] = agent_data

        robot_data = {'id': "this", 'type': "robot", 'pos': self.pos, 'location': self.model.get_location(self.pos),
                      'not_follow_request': self.not_follow_request,
                      'not_follow_locations': self.not_follow_locations, 'battery_level': self.battery, 'model': self,
                      'instruction_list': self.model.get_commands(self)}

        stakeholders['robot'] = robot_data

        env_data['stakeholders'] = stakeholders
        # env['']

        environment = {"time_of_day": 'day', "time": self.time,
                       "follower_avg_time_and_std_in_rooms": {'bathroom': (20, 10), 'kitchen': (60, 10),
                                                              'hall': (10, 5), 'bedroom': (200, 30)},
                       "no_of_follower_emergencies_in_past": 2,
                       "follower_health_score": 1,
                       "walls": self.model.wall_coordinates,
                       "things": self.model.things,
                       "things_robot_inaccessible": self.model.things_robot_inaccessible
                       }
        env_data['environment'] = environment

        # print("robot env: " + str(env))
        return env_data
