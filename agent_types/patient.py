from agent_types.home_agent import HomeAgent


class Patient(HomeAgent):
    def __init__(self, unique_id, name, model):
        super().__init__(unique_id, name, model, "patient")

    def step(self):
        self.move()

    def move(self):
        possible_steps = self.model.get_moveable_area(self.pos)
        print("possible steps: " + str(possible_steps))