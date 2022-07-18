from mesa_updated import Model, space, time

from common_functions.gen_id import GenId
from common_functions.visibilty import *

from agent_types.patient import Patient
from agent_types.robot import Robot
from agent_types.wall import Wall

PATIENT_2 = True


class Home(Model):
    def __init__(self):
        super().__init__()
        self.locations = None
        self.things = None

        self.init_locations()
        self.init_things()

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
        self.grid.place_agent(self.robot, (5, 7))

    def init_locations(self):
        self.locations = {}

        # Place the lower left coordinate first and the upper right coordinate second
        self.locations["Kitchen"] = [[(1, 1), (5, 3)], [(5, 4), (5, 4)]]
        self.locations["Living"] = [[(7, 1), (11, 3)], [(7, 4), (7, 4)]]
        self.locations["Hall"] = [[(1, 5), (11, 6)]]
        self.locations["Utility"] = [[(1, 8), (3, 11)], [(3, 7), (3, 7)]]
        self.locations["Bedroom"] = [[(5, 8), (8, 11)], [(5, 7), (5, 7)]]
        self.locations["Bathroom"] = [[(10, 8), (11, 11)], [(9, 8), (9, 8)]]

    def init_things(self):
        self.things = {}

        # add all the coordinate a thing should cover
        self.things['Couch'] = [(8, 2), (9, 2), (10, 2)]
        self.things['Chair'] = [(2, 2)]
        self.things['table'] = [(2, 3)]
        self.things['bed'] = [(8, 10), (8, 11)]
        self.things['charge_station'] = [(1, 9)]
        self.things['tub'] = [(11, 10), (11, 11)]

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

    def step(self):
        self.schedule.step()

    def visible_stakeholders(self, center_agent, visibility_radius):
        neighbors = self.grid.get_neighbors(center_agent.pos, moore=True, radius=visibility_radius)
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
        return visible_neighbors

    def get_moveable_area(self, pos):
        neighbourhood = self.grid.get_neighborhood(
            pos,
            moore=False,
            include_center=False
        )
        neighbours = self.grid.get_neighbors(
            pos,
            moore=True,
            include_center=False,
            radius= 1
        )

        possible_steps = []
        for step in neighbourhood:
            impossible = False
            for agent in neighbours:
                if step == agent.pos:
                    impossible = True
                    break
            if impossible:
                continue
            possible_steps.append(step)
        return possible_steps
