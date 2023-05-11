from agent_types.home_agent import HomeAgent

class Patient(HomeAgent):
    def __init__(self, unique_id, name, model, preferences):
        super().__init__(unique_id, name, model, "patient")
        self.steps = 0
        self.preferences = preferences

    def step(self):
        message = self.receive_message(self)
        if message is not None:
            request, code = message[0][0]
            self.respond(request, code)
        self.steps += 1

    def receive_message(self, receiver):
        return self.model.get_message(receiver)

    def respond(self, reason, code):
        pass

