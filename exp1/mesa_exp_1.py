from enum import Enum

from mesa import Agent, Model, space, time


class Direction(Enum):
    left = 0
    down = 1
    up = 2
    right = 3


class HomeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Robot(HomeAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.battery = 10

    def step(self):
        self.battery = self.battery - 1
        print("battery_lvl: " + str(self.battery))

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False
        )
        print(possible_steps)


class Patient(HomeAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

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
        self.robot = Robot(1, self)
        self.patient = Patient(2, self)
        self.grid = space.MultiGrid(100, 100, False)

        self.schedule = time.BaseScheduler(self)
        self.schedule.add(self.patient)
        self.schedule.add(self.robot)

        self.grid.place_agent(self.patient, (20, 20))
        self.grid.place_agent(self.robot, (20, 21))

    def step(self):
        self.schedule.step()


model = Home()
model.step()
