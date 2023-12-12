from agent_types.home_agent import HomeAgent
from agent_types.medication_robot import MessageCode

class Patient(HomeAgent):
    def __init__(self, unique_id, name, model, preferences):
        super().__init__(unique_id, name, model, "patient")
        self.reminders = 0
        self.preferences = preferences
        self.took_meds = True

    def step(self):
        message = self.receive_message(self)
        if message is not None:
            request, code = message[0][0]
            self.respond(request, code)


    def receive_message(self, receiver):
        return self.model.get_message(receiver)

    def did_take_meds(self):
        return self.took_meds

    def respond(self, request, code):
        if code == MessageCode.REMIND or code == MessageCode.FOLLOW_UP:
            self.took_meds = False
            self.model.pass_message(self.preferences["responses"][self.reminders], self, self.model.robot)
            if self.preferences["responses"][self.reminders] == 'SNOOZE':
                self.reminders += 1
            elif self.preferences["responses"][self.reminders] == 'ACKNOWLEDGE':
                if self.preferences["is_taking_meds"]:
                    self.took_meds = True
                self.reminders = 0

        pass

