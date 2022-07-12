from enum import Enum
import numpy as np

from mesa_updated import Agent, Model, space, time

PATIENT_2 = True

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


class GenId:
    def __init__(self, start):
        self.start = start
        self.current_id = start

    def get_id(self):
        ret_id = self.current_id
        self.current_id += 1

        return ret_id


class Home(Model):
    def __init__(self):
        super().__init__()
        self.locations = None
        self.init_locations()
        id_gen = GenId(1)
        self.robot = Robot(id_gen.get_id(), 'robot1', self)
        self.patient1 = Patient(id_gen.get_id(), 'patient1', self)
        if PATIENT_2:
            self.patient2 = Patient(id_gen.get_id(), 'patient2', self)
        self.grid = space.SingleGrid(13, 13, False)

        # adding agents
        self.schedule = time.BaseScheduler(self)
        self.schedule.add(self.patient1)
        if PATIENT_2:
            self.schedule.add(self.patient2)
        self.schedule.add(self.robot)

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

        self.grid.place_agent(self.patient1, (6, 9))
        if PATIENT_2:
            self.grid.place_agent(self.patient2, (8, 9))
        self.grid.place_agent(self.robot, (5, 6))

    def init_locations(self):
        self.locations = {}

        # Place the lower left coordinate first and the upper right coordinate second
        self.locations["Kitchen"] = [[(1, 1), (5, 3)], [(5, 4), (5, 4)]]
        self.locations["Living"] = [[(7, 1), (11, 3)], [(7, 4), (7, 4)]]
        self.locations["Hall"] = [[(1, 5), (11, 6)]]
        self.locations["Utility"] = [[(1, 8), (3, 11)], [(3, 7), (3, 7)]]
        self.locations["Bedroom"] = [[(5, 8), (8, 11)], [(5, 7), (5, 7)]]
        self.locations["Bathroom"] = [[(10, 8), (11, 11)], [(9, 8), (9, 8)]]

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

    def step(self):
        self.schedule.step()

    def add_vertical_wall(self, x, ystart, yend, id_gen):
        coordinates = [(x, y) for y in range(ystart, yend + 1)]
        wall, id_gen = self.place_wall(coordinates, id_gen)
        return wall, id_gen

    def add_horizontal_wall(self, xstart, xend, y, id_gen):
        coordinates = [(x, y) for x in range(xstart, xend + 1)]
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

    def visible_stakeholders_to_robot(self):
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


model = Home()
model.step()
model.visible_stakeholders_to_robot()
print(model.get_location((5, 6)))
print(model.get_location((5, 7)))