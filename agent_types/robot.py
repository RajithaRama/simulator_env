from agent_types.home_agent import HomeAgent
import numpy as np

SELF_CHARGING = True


class Robot(HomeAgent):
    def __init__(self, unique_id, name, model, follower_name):
        super().__init__(unique_id, name, model, "robot")
        self.battery = 50
        self.time = 0
        self.last_seen_location = None
        self.last_seen_time = None
        self.follower_name = follower_name
        self.not_follow_request = False
        self.not_follow_locations = []

    def step(self):
        if self.pos in self.model.things['charge_station']:
            self.battery += 3
        else:
            self.battery -= 1
        print("battery_lvl: " + str(self.battery))
        env = self.get_env_data()
        # self.follow(env)
        self.next_action(env)
        self.time += 1

    def next_action(self, env):

        buffered_instructions = self.model.get_commands(self)

        possible_actions = []

        # get and apply buffered_instructions
        if len(buffered_instructions):
            # If user istruct to make clear, robot try to move away from the said user
            for instruction in buffered_instructions:
                # instruction = (command, giver)
                # add make clear instruction to possible action list
                if 'make_clear' == instruction[0]:
                    possible_actions.append((self.move_away, instruction[1]))
                if 'do_not_follow_to' in instruction[0]:
                    ins_split = instruction[0].split('__')
                    if ins_split[1] in self.model.locations.keys():
                        self.do_not_follow_to(to_location=ins_split[1], follower=instruction[1])
                if 'continue' == instruction[0] and self.not_follow_request:
                    self.remove_not_follow()

        # get visible neighbours and set follower
        visible_neighbors = self.model.visible_stakeholders(self, 3)

        follower = None
        for neighbor in visible_neighbors:
            if neighbor.id == self.follower_name:
                follower = neighbor
                self.last_seen_location = follower.pos
                old_last_seen_time = self.last_seen_time
                self.last_seen_time = self.time

        # Follow or go to last seen
        if follower:
            possible_actions.append((self.follow, follower))
        else:
            possible_actions.append((self.go_to_last_seen, ))

        # if follower in a restricted area stay
        if follower and (self.model.get_location(follower.pos) in self.not_follow_locations):
            possible_actions.append(self.move(self.pos))

        if SELF_CHARGING:
            possible_actions.append((self.go_to_charge_station, ))

        self.make_final_decision(possible_actions, env)

    def make_final_decision(self, possible_actions, env):
        # Check for low battery
        if self.battery < 20 or (self.battery < 80 and (self.pos in self.model.things['charge_station'])):
            for action in possible_actions:
                if self.go_to_charge_station == action[0]:
                    action[0](*action[1:])
                    return



        # Check for move away
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

    def do_not_follow_to(self, to_location, follower):
        self.not_follow_request = True
        self.not_follow_locations.append(to_location)


    def remove_do_not_follow(self):
        self.not_follow_request = False
        self.not_follow_locations.pop()

    def follow(self, follower):
        possible_steps = self.model.get_moveable_area(self.pos, [self])

        distances = {}
        for step in possible_steps:
            distances[self.model.get_shortest_distance(step, follower.pos, [self, follower])] = step

        next_pos = distances[min(distances.keys())]

        self.move(next_pos)

    def go_to_pos(self, pos, ignore_agents=None):
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

        self.move(next_pos)

    def go_to_charge_station(self):
        self.go_to_pos(self.model.things['charge_station'][0], [self])

    def go_to_last_seen(self):
        possible_locations = [self.last_seen_location]

        while len(possible_locations):
            try:
                possible_pos = possible_locations.pop(0)
                self.go_to_pos(possible_pos, [self])
            except EnvironmentError:
                possible_locations.extend(self.model.get_moveable_area(possible_pos))
                continue
            break

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

        # print("robot env: " + str(env))
        return env
