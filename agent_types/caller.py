from enum import Enum

from agent_types.home_agent import HomeAgent

class CALLER_TYPE(Enum):
    FAMILY = 1
    FRIEND = 2
    CAREGIVER = 3
    DOCTOR = 4
    OTHER = 5

class Caller(HomeAgent):
    def __init__(self, unique_id, name, model, commands, type, calling_resident):
        super().__init__(unique_id, name, model, "caller")
        self.robot_commands = commands
        self.steps = 0
        self.type = type
        self.calling_resident = calling_resident
        self.call_declined = False
        self.instruction_sent = 0

    def step(self):
        message = self.receive_message(self)
        
        if message is not None:
            reason, code = message[0][0]
            if code == -1:
                self.steps -= 1
                self.nstruction_sent = 0

            if code == -2:
                self.call_declined = True
                self.steps -= 1
                self.instruction_sent = 0

        if not self.instruction_sent:
            self.instruction_sent = self.send_message()
            return
        
        self.instruction_sent = 0
    
    def receive_message(self, receiver):
        return self.model.get_message(receiver)

    def send_message(self):
        if self.call_declined:
            return 0
        
        try:
            next_command = self.robot_commands[self.steps]
        except IndexError:
            return 0

        try:
            if next_command[0] != '':
                self.model.pass_message(next_command, self, self.model.robot)
                print("Caller: " + str(next_command))
        except Exception as e:
            print(e)
            return 0

        self.steps += 1
        return 1