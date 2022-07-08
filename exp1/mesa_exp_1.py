from enum import Enum
import numpy as np

from mesa import Agent, Model, space, time

import numpy as np
def _bresenhamline_nslope(slope):
    """
    Normalize slope for Bresenham's line algorithm.
    """
    scale = np.amax(np.abs(slope), axis=1).reshape(-1, 1)
    zeroslope = (scale == 0).all(1)
    scale[zeroslope] = np.ones(1)
    normalizedslope = np.array(slope, dtype=np.double) / scale
    normalizedslope[zeroslope] = np.zeros(slope[0].shape)
    return normalizedslope

def _bresenhamlines(start, end, max_iter):
    """
    Returns npts lines of length max_iter each. (npts x max_iter x dimension)

    array([[[ 3,  1,  8,  0],
            [ 2,  1,  7,  0],
            [ 2,  1,  6,  0],
            [ 2,  1,  5,  0],
            [ 1,  0,  4,  0],
            [ 1,  0,  3,  0],
            [ 1,  0,  2,  0],
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  0]],
    <BLANKLINE>
           [[ 0,  0,  2,  0],
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  0],
            [ 0,  0, -1,  0],
            [ 0,  0, -2,  0],
            [ 0,  0, -3,  0],
            [ 0,  0, -4,  0],
            [ 0,  0, -5,  0],
            [ 0,  0, -6,  0]]])
    """
    if max_iter == -1:
        max_iter = np.amax(np.amax(np.abs(end - start), axis=1))
    npts, dim = start.shape
    nslope = _bresenhamline_nslope(end - start)

    # steps to iterate on
    stepseq = np.arange(1, max_iter + 1)
    stepmat = np.tile(stepseq, (dim, 1)).T

    # some hacks for broadcasting properly
    bline = start[:, np.newaxis, :] + nslope[:, np.newaxis, :] * stepmat

    # Approximate to nearest int
    return np.array(np.rint(bline), dtype=start.dtype)

def bresenhamline(start, end, max_iter=5):
    """
    Returns a list of points from (start, end] by ray tracing a line b/w the
    points.
    Parameters:
        start: An array of start points (number of points x dimension)
        end:   An end points (1 x dimension)
            or An array of end point corresponding to each start point
                (number of points x dimension)
        max_iter: Max points to traverse. if -1, maximum number of required
                  points are traversed

    Returns:
        linevox (n x dimension) A cumulative array of all points traversed by
        all the lines so far.
    """

    # Return the points as a single array
    return _bresenhamlines(start, end, max_iter).reshape(-1, start.shape[-1])

class Direction(Enum):
    left = 0
    down = 1
    up = 2
    right = 3


class Wall(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'wall'


class HomeAgent(Agent):
    def __init__(self, unique_id, name, model, type):
        super().__init__(unique_id, model)
        self.type = type
        self.id = name


class Robot(HomeAgent):
    def __init__(self, unique_id, name, model):
        super().__init__(unique_id, name, model, "robot")
        self.battery = 10

    def step(self):
        self.battery = self.battery - 1
        print("battery_lvl: " + str(self.battery))
        self.get_env_data()
        self.move()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False
        )
        print(possible_steps)

    def get_env_data(self):
        env = {}
        agents = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            radius=2
        )

        stakeholders = []
        for agent in agents:
            # print(agent.type)
            agent_data = {}
            if agent.type == 'wall':
                continue
            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            stakeholders.append(agent_data)
        env['stakeholders'] = stakeholders

        print(env)


class Patient(HomeAgent):
    def __init__(self, unique_id, name, model):
        super().__init__(unique_id, name, model, "patient")

    def step(self):
        self.move()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False
        )
        print(possible_steps)


class Home(Model):
    def __init__(self):
        super().__init__()
        self.robot = Robot(1, 'robot1', self)
        self.patient = Patient(2, 'patient1', self)
        self.grid = space.SingleGrid(13, 13, False)

        # adding agents
        self.schedule = time.BaseScheduler(self)
        self.schedule.add(self.patient)
        self.schedule.add(self.robot)

        # adding walls
        # house
        self.walls = []
        wall, end_id = self.add_vertical_wall(0, 0, 12, 3)
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

        self.grid.place_agent(self.patient, (6, 9))
        self.grid.place_agent(self.robot, (5, 6))

    def visible_stakeholders(self):
        neighbors = self.grid.get_neighbors(self.robot.pos, moore=True, radius=3)
        print("neigh: " + str(neighbors))

        coordinate_neighbors = {}
        walls = {}
        for neighbor in neighbors:
            if neighbor.type == 'wall':
                walls[neighbor.pos] = neighbor
            else:
                coordinate_neighbors[neighbor.pos] = neighbor

        print(coordinate_neighbors)

        visible_neighbors = []
        for coordinate, neighbor in coordinate_neighbors.items():
            robot_pos = np.array([np.array(self.robot.pos)])
            print(robot_pos.shape)
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

        print("visible: " + str(visible_neighbors))


    def step(self):
        self.schedule.step()

    def add_vertical_wall(self, x, ystart, yend, start_id):
        coordinates = [(x, y) for y in range(ystart, yend + 1)]
        wall, end_id = self.place_wall(coordinates, start_id)
        return wall, end_id

    def add_horizontal_wall(self, xstart, xend, y, start_id):
        coordinates = [(x, y) for x in range(xstart, xend + 1)]
        wall, end_id = self.place_wall(coordinates, start_id)
        return wall, end_id

    def place_wall(self, coordinates, start_id):
        wall = []
        for point in coordinates:
            point_wall = Wall(start_id, self)
            self.schedule.add(point_wall)
            self.grid.place_agent(point_wall, (point[0], point[1]))
            wall.append(point_wall)
            start_id += 1
        return wall, start_id


model = Home()
model.step()
model.visible_stakeholders()
