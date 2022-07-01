from enum import Enum

from mesa import Agent, Model, space, time


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

        #bathroom
        wall, end_id = self.add_vertical_wall(9, 9, 11, end_id)
        self.walls.append(wall)




        self.grid.place_agent(self.patient, (10, 10))
        self.grid.place_agent(self.robot, (10, 11))

    def step(self):
        self.schedule.step()

    def add_vertical_wall(self, x, ystart, yend, start_id):
        coordinates = [(x, y) for y in range(ystart, yend+1)]
        wall, end_id = self.place_wall(coordinates, start_id)
        return wall, end_id

    def add_horizontal_wall(self, xstart, xend, y, start_id):
        coordinates = [(x, y) for x in range(xstart, xend+1)]
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
