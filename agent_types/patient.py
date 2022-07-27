from agent_types.home_agent import HomeAgent


class Patient(HomeAgent):
    def __init__(self, unique_id, name, model, path):
        super().__init__(unique_id, name, model, "patient")
        self.path = path
        self.steps = 0

    def step(self):
        self.move()

    def move(self):
        # possible_steps = self.model.get_moveable_area(self.pos)
        # print("possible steps: " + str(possible_steps))
        next_pos = self.path[self.steps]

        try:
            self.model.grid.move_agent(self, next_pos)
        except Exception as e:
            print(e)
            self.model.grid.move_agent(self, self.pos)
            self.model.give_command('make_clear', self, self.model.robot)
            return

        self.steps += 1