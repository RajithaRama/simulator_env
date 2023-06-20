import sys
from enum import Enum

from mesa_updated import Model, space, time

from common_functions.gen_id import GenId
from common_functions.visibilty import *

from agent_types.medication_patient import Patient
# from agent_types.care_worker import CareWorker
from agent_types.medication_robot import Robot
from agent_types.wall import Wall


from collections import deque

PATIENT_2 = True

GRID_WIDTH = 13
GRID_HEIGHT = 13


class Home(Model):

    MINS_PER_STEP = 1
    def __init__(self, no_patients, patient_starts, robot_start, patient_paths, patient_healths, patient_preferences, governor_conf, time_of_day, med_info, robot_character, worker_data=None, timer_data=[]):
        super().__init__()
        self.things_robot_inaccessible = None
        self.locations = None
        self.things = None

        self.init_locations()
        self.init_things()
        self.time_of_day = time_of_day
        self.instructions = {}
        self.message_history = []
        self.patient_healths = patient_healths
        self.medication_info = med_info

        id_gen = GenId(1)

        # Init robot
        self.robot = Robot(id_gen.get_id(), 'robot1', self, 'patient_0', governor_conf, 100, character=robot_character ,timer_data=timer_data)

        # Init_stakeholders
        self.stakeholders = []
        for i in range(no_patients):
            self.stakeholders.append(Patient(id_gen.get_id(), 'patient_' + str(i), self, patient_preferences[i]))

        # init care worker
        # if worker_data is not None:
        #     self.stakeholders.append(CareWorker(id_gen.get_id(), 'care_worker', self, worker_data['path'], worker_data['preferences']))

        self.grid = space.SingleGrid(GRID_WIDTH, GRID_HEIGHT, False)

        # adding agents
        self.schedule = time.BaseScheduler(self)

        for stakeholder in self.stakeholders:
            self.schedule.add(stakeholder)

        self.schedule.add(self.robot)

        self.wall_coordinates = []

        # adding walls
        # house
        self.walls = []
        wall, end_id = self.add_vertical_wall(0, 0, 12, id_gen)
        self.walls.append(wall)
        wall, end_id = self.add_vertical_wall(12, 0, 12, end_id)
        self.walls.append(wall)
        wall, end_id = self.add_horizontal_wall(1, 11, 0, end_id)
        self.walls.append(wall)
        wall, end_id = self.add_horizontal_wall(1, 11, 12, end_id)
        self.walls.append(wall)

        # Living room
        wall, end_id = self.add_vertical_wall(6, 1, 4, end_id)
        self.walls.append(wall)
        wall, end_id = self.add_horizontal_wall(8, 11, 4, end_id)
        self.walls.append(wall)

        # kitchen
        wall, end_id = self.add_horizontal_wall(1, 4, 4, end_id)
        self.walls.append(wall)

        # utility room
        wall, end_id = self.add_vertical_wall(4, 7, 11, end_id)
        self.walls.append(wall)
        wall, end_id = self.add_horizontal_wall(1, 2, 7, end_id)
        self.walls.append(wall)

        # bedroom
        wall, end_id = self.add_horizontal_wall(6, 11, 7, end_id)
        self.walls.append(wall)

        # bathroom
        wall, end_id = self.add_vertical_wall(9, 9, 11, end_id)
        self.walls.append(wall)

        for i in range(no_patients):
            self.grid.place_agent(self.stakeholders[i], patient_starts[i])

        if worker_data is not None:
            self.grid.place_agent(self.stakeholders[-2], worker_data['path'][0][0])

        self.grid.place_agent(self.robot, robot_start)

    def init_locations(self):
        self.locations = {}

        # Place the lower left coordinate first and the upper right coordinate second
        self.locations["kitchen"] = [[(1, 1), (5, 3)], [(5, 4), (5, 4)]]
        self.locations["living"] = [[(7, 1), (11, 3)], [(7, 4), (7, 4)]]
        self.locations["hall"] = [[(1, 5), (11, 6)]]
        self.locations["utility"] = [[(1, 8), (3, 11)], [(3, 7), (3, 7)]]
        self.locations["bedroom_close_bed"] = [[(7, 10), (8, 11)]]
        self.locations["bedroom"] = [[(5, 8), (8, 9)], [(5, 10), (6, 11)], [(5, 7), (5, 7)]]
        self.locations["bathroom"] = [[(10, 8), (11, 11)], [(9, 8), (9, 8)]]

    def init_things(self):
        self.things = {}

        # add all the coordinate a thing should cover
        self.things['couch'] = [(8, 2), (9, 2), (10, 2)]
        self.things['chair'] = [(2, 2)]
        self.things['table'] = [(3, 2)]
        self.things['bed'] = [(8, 10), (8, 11)]
        self.things['charge_station'] = [(1, 9)]
        self.things['tub'] = [(11, 10), (11, 11)]

        self.things_robot_inaccessible = ['couch', 'chair', 'table', 'bed', 'tub']

    def get_location(self, pos):
        location_name = None
        for location, area_coordinates in self.locations.items():
            for points in area_coordinates:
                if points[0][0] <= pos[0] <= points[1][0] and points[0][1] <= pos[1] <= points[1][1]:
                    if location_name:
                        raise EnvironmentError("Overlapping location names for: " + str(pos) + ". "
                                               + location_name + " and " + location)
                    location_name = location
        if location_name:
            return location_name
        else:
            raise EnvironmentError("Agent Location Unknown for position: " + str(pos))

    def get_things(self, pos):
        things = []

        for thing, coordinates in self.things.items():
            if pos in coordinates:
                things.append(thing)

        return things

    def get_stakeholder(self, name):
        for stakeholder in self.stakeholders:
            if stakeholder.id == name:
                return stakeholder

    def add_vertical_wall(self, x, ystart, yend, id_gen):
        coordinates = [(x, y) for y in range(ystart, yend + 1)]
        self.wall_coordinates.append(coordinates)
        wall, id_gen = self.place_wall(coordinates, id_gen)
        return wall, id_gen

    def add_horizontal_wall(self, xstart, xend, y, id_gen):
        coordinates = [(x, y) for x in range(xstart, xend + 1)]
        self.wall_coordinates.append(coordinates)
        wall, id_gen = self.place_wall(coordinates, id_gen)
        return wall, id_gen

    def place_wall(self, coordinates, id_gen):
        wall = []
        for point in coordinates:
            point_wall = Wall(id_gen.get_id(), self)
            self.schedule.add(point_wall)
            self.grid.place_agent(point_wall, (point[0], point[1]))
            wall.append(point_wall)
        return wall, id_gen

    def step(self):
        self.schedule.step()

    def visibility_ab(self, a, b, visibility_radius):
        """Visibility of pos b from pos a"""
        neighbors = self.grid.get_neighbors(a, moore=True, radius=visibility_radius)
        # print("neigh: " + str(neighbors))

        walls = {}
        for neighbor in neighbors:
            if neighbor.type == 'wall':
                walls[neighbor.pos] = neighbor

        visible_line = bresenhamline(np.array([np.array(a)]), np.array([np.array(b)]), -1)

        # print(visible_line)
        visible = True
        for point in visible_line:
            if tuple(point) in walls.keys():
                visible = False

        return visible

    def visible_stakeholders(self, center_agent_pos, visibility_radius):
        neighbors = self.grid.get_neighbors(center_agent_pos, moore=True, radius=visibility_radius)
        # print("neigh: " + str(neighbors))

        coordinate_neighbors = {}
        walls = {}
        for neighbor in neighbors:
            if neighbor.type == 'wall':
                walls[neighbor.pos] = neighbor
            else:
                coordinate_neighbors[neighbor.pos] = neighbor

        # print(coordinate_neighbors)

        visible_neighbors = []
        for coordinate, neighbor in coordinate_neighbors.items():
            robot_pos = np.array([np.array(self.robot.pos)])
            # print(robot_pos.shape)
            # robot_pos = robot_pos.reshape(1, 1)
            # print(robot_pos.shape)
            visible_line = bresenhamline(np.array([np.array(self.robot.pos)]), np.array([np.array(neighbor.pos)]), -1)

            # print(visible_line)
            visible = True
            for point in visible_line:
                if tuple(point) in walls.keys():
                    visible = False

            if visible:
                visible_neighbors.append(neighbor)

        # print("visible: " + str(visible_neighbors))
        return visible_neighbors

    def get_moveable_area(self, pos, ignore_agents=None):
        """ from_agent: agent that is trying to move"""
        neighbourhood = self.grid.get_neighborhood(
            pos,
            moore=False,
            include_center=True
        )
        neighbours = self.grid.get_neighbors(
            pos,
            moore=True,
            include_center=False,
            radius=1
        )

        possible_steps = []
        for step in neighbourhood:
            impossible = False
            for agent in neighbours:
                # Not possible if an agent is in the position. Ignore the agents in the ignore list.
                if step == agent.pos and \
                        (all([agent.unique_id != ignore_agent.unique_id for ignore_agent in
                              ignore_agents]) if ignore_agents else 1):
                    impossible = True
                    break
            for thing_id, thing_coordinates in self.things.items():
                # Avoid things too. If any ignore list agent on a thing, ignore that thing as well.
                if ignore_agents and any([ignore_agent.pos in thing_coordinates for ignore_agent in ignore_agents]):
                    break
                if (step in thing_coordinates) and (thing_id in self.things_robot_inaccessible):
                    impossible = True
                    break
            if impossible:
                continue
            possible_steps.append(step)
        return possible_steps

    def get_shortest_distance(self, current, dest, ignore_agents=None):

        i, j = current
        x, y = dest

        visited = [[False for x in range(GRID_HEIGHT)] for y in range(GRID_HEIGHT)]

        q = deque()

        # Mark source as visited
        visited[i][j] = True

        # (i, j, distance from the source)
        q.append((i, j, 0))

        min_dist = sys.maxsize

        while q:
            (i, j, dist) = q.popleft()

            if i == x and j == y:
                min_dist = dist
                break
            # Breath-first search
            possible_moves = self.get_moveable_area((i, j), ignore_agents=ignore_agents)
            for move in possible_moves:
                if not visited[move[0]][move[1]]:
                    visited[move[0]][move[1]] = True
                    q.append((move[0], move[1], dist + 1))

        if min_dist != sys.maxsize:
            return min_dist
        else:
            return -1



    def turn_off_lights(self):
        self.time_of_day = 'night'

    def pass_message(self, command, giver, receiver):
        self.instructions.setdefault(receiver, []).append([command, giver])
        if giver.type == 'robot':
            self.message_history.append([command[0], giver.id, receiver.id, self.schedule.steps])
            print('Passing message: "' + command[0] + '" from ' + giver.id + ' to ' + receiver.id)
        else:
            self.message_history.append([command, giver.id, receiver.id, self.schedule.steps])
            print('Passing message: "' + command + '" from ' + giver.id + ' to ' + receiver.id)


    def get_message(self, receiver):
        instructions = None
        if receiver in self.instructions.keys():
            instructions = self.instructions[receiver]
            self.instructions.pop(receiver)
        return instructions


    def alert_careworker(self, message):
        self.message_history.append([message, 'robot1', "Care-worker", self.schedule.steps])
        print('Alerting care-worker: ' + message)


class MedImpact(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3