from agent_types.home_agent import HomeAgent
import numpy as np


class Robot(HomeAgent):
    def __init__(self, unique_id, name, model, follower_name):
        super().__init__(unique_id, name, model, "robot")
        self.battery = 10
        self.time = 0
        self.last_seen_location = None
        self.last_seen_time = None
        self.follower_name = follower_name

    def step(self):
        self.battery = self.battery - 1
        print("battery_lvl: " + str(self.battery))
        env = self.get_env_data()
        # self.follow(env)
        self.next_action(env)

    def next_action(self, env):

        buffered_instructions = self.model.get_commands(self)

        possible_actions = []

        if len(buffered_instructions):
            # If user istruct to make clear, robot try to move away from the said user
            for instruction in buffered_instructions:
                # instruction = (command, giver)
                if 'make_clear' == instruction[0]:
                    possible_actions.append((self.move_away, instruction[1]))

        visible_neighbors = self.model.visible_stakeholders(self, 3)

        follower = None
        for neighbor in visible_neighbors:
            if neighbor.id == self.follower_name:
                follower = neighbor

        if follower:
            possible_actions.append((self.follow, follower))
        else:
            possible_actions.append((self.go_to_pos, self.last_seen_location))

        self.make_final_decision(possible_actions)

    def make_final_decision(self, possible_actions):
        for action in possible_actions:
            if self.move_away == action[0]:
                action[0](*action[1:])
                return

        possible_actions[0][0](*possible_actions[0][1:])

    def move_away(self, follower):
        """ pos - position to move away from"""
        possible_steps = self.model.get_moveable_area(self.pos, [self])

        distances = {}
        for step in possible_steps:
            distances[self.model.get_shortest_distance(step, follower.pos, [self, follower])] = step

        next_pos = distances[max(distances.keys())]

        self.move(next_pos)

    def follow(self, follower):
        possible_steps = self.model.get_moveable_area(self.pos, [self])

        distances = {}
        for step in possible_steps:
            distances[self.model.get_shortest_distance(step, follower.pos, [self, follower])] = step

        next_pos = distances[min(distances.keys())]

        self.move(next_pos)

    def go_to_pos(self, pos):
        possible_steps = self.model.get_moveable_area(self.pos)

        distances = {}
        for step in possible_steps:
            distances[self.model.get_shortest_distance(step, pos)] = step

        next_pos = distances[min(distances.keys())]

        self.move(next_pos)

    def move(self, pos):
        self.model.grid.move_agent(self, pos)

    def get_env_data(self):
        env = {}
        visible_stakeholders = self.model.visible_stakeholders(self, 3)

        stakeholders = []
        for agent in visible_stakeholders:
            # print(agent.type)
            agent_data = {}
            if agent.type == 'wall':
                continue
            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            stakeholders.append(agent_data)
        env['stakeholders'] = stakeholders

        print("robot env: " + str(env))
        return env
