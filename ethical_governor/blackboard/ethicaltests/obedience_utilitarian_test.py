# To-Do:
from math import sqrt

import blackboard.ethicaltests.ethical_test as ethical_test


class UtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        robot_data = data.get_stakeholders_data()["robot"]
        human_data = data.get_stakeholders_data()["user"]
        environment_data = data.get_environment_data()
        world = WorldModel(robot_location=robot_data[0], robot_goal=robot_data[1], user_location=human_data[0],
                           user_init_position=environment_data["user_init_location"], user_state=human_data[1],
                           danger_location=environment_data["danger"], danger_radius=environment_data["danger_radius"])

        for action in data.get_actions():
            logger.info('Testing action: ' + str(action.value))
            action_value = action.value
            logger.info('Simulating action..')
            is_harmful_human, is_harmful_robot, is_not_obedient = world.outcome(action_value)
            if is_harmful_human:
                logger.info('Harm to human detected.')
            if is_harmful_robot:
                logger.info('Harm to robot detected.')
            if is_not_obedient:
                logger.info('Robot disobedience event detected.')
            # logger.info()
            logger.info('simulation_completed')

            obedience = -1 if is_not_obedient else 1
            safety_human = 0 if is_harmful_human else 1
            safety_robot = 0 if is_harmful_robot else 1

            logger.info('User safety utility for action ' + str(action.value) + ': ' + str(safety_human))
            logger.info('Robot safety utility for action ' + str(action.value) + ': ' + str(safety_robot))
            logger.info('Robot obedience utility for action ' + str(action.value) + ': ' + str(obedience))

            self.output[action] = {self.output_names[0]: obedience, self.output_names[1]: safety_human,
                                   self.output_names[2]: safety_robot}

        logger.info(__name__ + ' finished.')


class WorldModel:

    def __init__(self, size=[5, 5], robot_location=[0, 0], user_location=[0, 4], user_init_position=[0, 4],
                 user_state="walking", danger_location=[4, 4], danger_radius=1, robot_goal=[4, 1]):

        self.size = size
        self.danger = danger_location
        self.robot_goal = robot_goal
        self.danger_radius = danger_radius
        self.user_location = user_location
        self.robot_location = robot_location

        self.human = HumanModel(user_location, user_init_position, user_state)
        self.robot = RobotModel(robot_location)

    def outcome(self, temp_goal):
        harm_human = False
        harm_robot = False
        disobeying_robot = False

        if temp_goal != self.robot_goal:
            disobeying_robot = True

        if self.human.is_in_danger(self.danger, self.danger_radius, temp_goal):
            if not self._can_stop_human(temp_goal):
                harm_human = True

        distance_to_danger = sqrt((temp_goal[1] - self.danger[1]) ** 2 + (temp_goal[0] - self.danger[0]) ** 2)
        if distance_to_danger < self.danger_radius:
            harm_robot = True

        return harm_human, harm_robot, disobeying_robot

    def _can_stop_human(self, temp_goal):
        time_robot = self.robot.time_to_new_location(temp_goal)
        time_human = self.human.time_to_new_location(temp_goal)
        shortest_distant_to_goal = self.human.simulate_path(temp_goal)
        return True if (time_robot <= time_human) and \
                       (shortest_distant_to_goal < 0.5) else False


class HumanModel:

    def __init__(self, current_location, initial_location, state):
        self.location = current_location
        self.initial_location = initial_location
        self.speed = 1  # meter for step
        self.human_state = state

    def simulate_path(self, goal):
        """Shortest distance to the human path from a location"""
        shortest_distance_to_danger = abs(
            (self.location[0] - self.initial_location[0]) * (self.initial_location[1] - goal[1])
            - (self.initial_location[0] - goal[0]) * (self.location[1] - self.initial_location[1])) / sqrt(
            (self.location[0] - self.initial_location[0]) ** 2
            + (self.location[1] - self.initial_location[1]) ** 2)

        return shortest_distance_to_danger

    def is_in_danger(self, danger, danger_radius, robot_location):
        distance_to_robot = sqrt(
            (robot_location[1] - self.location[1]) ** 2 + (robot_location[0] - self.location[0]) ** 2)
        distance_to_danger = sqrt((danger[1] - self.location[1]) ** 2 + (danger[0] - self.location[0]) ** 2)

        if self.simulate_path(danger) < danger_radius and self.human_state == "walking":
            if distance_to_robot < 1 and distance_to_danger > 1:
                return False
            else:
                return True
        else:
            return False

    def time_to_new_location(self, x):
        distance = sqrt((x[1] - self.location[1]) ** 2 + (x[0] - self.location[0]) ** 2)
        time = distance / self.speed
        return time


class RobotModel:

    def __init__(self, current_location):
        self.location = current_location
        # self.initial_location = initial_location
        self.speed = 2.5  # meter for step

    def time_to_new_location(self, x):
        distance = sqrt((x[1] - self.location[1]) ** 2 + (x[0] - self.location[0]) ** 2)
        time = distance / self.speed
        return time
