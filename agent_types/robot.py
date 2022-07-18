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
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False
        )
        print(possible_steps)

    def get_env_data(self):
        env = {}
        agents = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            radius=2
        )

        stakeholders = []
        for agent in agents:
            # print(agent.type)
            agent_data = {}
            if agent.type == 'wall':
                continue
            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            stakeholders.append(agent_data)
        env['stakeholders'] = stakeholders

        print(env)
