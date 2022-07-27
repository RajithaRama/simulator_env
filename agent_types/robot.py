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
        self.follow(env)

        self.move()

    def follow(self, env):
        possible_steps = self.model.get_moveable_area(self.pos)

        buffered_instructions = self.model.get_commands(self)

        dist_min = True

        if len(buffered_instructions):
            # If user istruct to make clear. it robot try to maximize the space user have. Otherwise it try to minimize so
            # that it can closely monitor
            for instruction in buffered_instructions:
                if 'make_clear' == instruction[0]:
                    dist_min = False

        visible_neighbors = self.model.visible_stakeholders(self, 3)

        follower = None
        for neighbor in visible_neighbors:
            if neighbor.id == self.follower_name:
                follower = neighbor

        distances = {}
        for step in possible_steps:
            distances[self.model.get_manhatton_dist(step, follower.pos)] = step

        if dist_min:
            next_pos = distances[min(distances.keys())]
        else:
            next_pos = distances[max(distances.keys())]

        self.model.grid.move_agent(self, next_pos)


    def move(self):
        possible_steps = self.model.get_moveable_area(self.pos)
        print("poss steps robot: " + str(possible_steps))

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
