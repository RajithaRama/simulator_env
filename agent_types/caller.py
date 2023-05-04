from enum import Enum

from agent_types.home_agent import HomeAgent

class CALLER_TYPE(Enum):
    FAMILY = 1
    FRIEND = 2
    CAREGIVER = 3
    DOCTOR = 4

class Caller(HomeAgent):
    def __init__(self, unique_id, name, model, commands, type):
        super().__init__(unique_id, name, model, "caller")
        self.robot_commands = commands
        self.steps = 0
        self.type = type


    def step(self):
        message, code = self.receive_message(self)
        self.call()

    def receive_message(self, sender):
        return self.model.get_message()
    def send_message(self):
        try:
            next_command = self.path[self.steps]
        except IndexError:
            return

        try:
            if next_command[0] != '':
                self.model.pass_message(next_command, self, self.model.robot)
        except Exception as e:
            print(e)
            self.model.give_command('move_away', self, self.model.robot)
            return

        self.steps += 1