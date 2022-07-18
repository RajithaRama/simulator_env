from mesa_updated import Agent


class HomeAgent(Agent):
    def __init__(self, unique_id, name, model, type):
        super().__init__(unique_id, model)
        self.type = type
        self.id = name
