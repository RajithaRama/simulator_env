from mesa_updated import Agent


class Wall(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'wall'
