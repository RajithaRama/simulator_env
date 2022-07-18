from agent_types.home_agent import HomeAgent


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
        possible_steps = self.model.get_moveable_area(self.pos)
        print("poss steps robot: " + str(possible_steps))

    def get_env_data(self):
        env = {}
        visible_stakeholders = self.model.visible_stakeholders(self, 3)

        stakeholders = []
        for agent in visible_stakeholders:
            # print(agent.type)
            agent_data = {}
            if agent.type == 'wall':
                continue
            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            stakeholders.append(agent_data)
        env['stakeholders'] = stakeholders

        print("robot env: " + str(env))

