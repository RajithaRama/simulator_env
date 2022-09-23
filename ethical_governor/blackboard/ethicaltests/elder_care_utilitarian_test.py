import numpy as np

import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test
import agent_types.robot as ROBOT


class ElderCareUtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)
        self.instruction_function_map = {
            'do_not_follow_to': [False, ROBOT.Robot.follow],
            'continue': [True, ROBOT.Robot.follow],
            'move_away': [True, ROBOT.Robot.move_away]
        }

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        env = data.get_environment_data()
        stakeholder_data = data.get_stakeholders_data()

        for action in data.get_actions():
            utils = {}

            logger.info('Testing action: ' + str(action.value))

            logger.info('Calculating autonomy utility for stakeholders')
            autonomy_utility = self.get_autonomy_utility(env=env, stakeholder_data=stakeholder_data, action=action,
                                                         logger=logger)
            logger.info('Autonomy utilities for action ' + str(action.value) + ': ' + str(autonomy_utility))
            utils['autonomy'] = autonomy_utility

            logger.info('Calculating well-being utility for stakeholders')
            wellbeing_util = self.get_wellbeing_utility(env=env, stakeholder_data=stakeholder_data, action=action,
                                                        logger=logger)
            logger.info('Wellbeing utilities for action ' + str(action.value) + ': ' + str(wellbeing_util))

            utils['wellbeing'] = wellbeing_util

            out = {}
            for util_type, values in utils.items():
                for stakeholder, util_value in values:
                    col_name = stakeholder + '_' + util_type
                    out[col_name] = util_value
            self.output[action] = out

    def get_autonomy_utility(self, env, stakeholder_data, action, logger):
        """
        Calculating autonomy  values for stakeholders.
        When the robot does not follow a user command, autonomy value for that user is -1, if it follows 1 and the
        default is 0.
        - return: list with (stakeholder_id, autonomy utility) tuples
        """
        # Simulating next pos and visible lines
        next_pos = action.value[0](*action.value[1:], act=False)
        # visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        # center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        # visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]
        robot_model = stakeholder_data['robot']['model']
        instruction_list = robot_model.model.get_commands(self)

        stakholder_autonomy_values = []

        for stakeholder in stakeholder_data.keys():
            # skip for robot
            if stakeholder == 'robot':
                continue

            autonomy_utility = 0

            for ins, giver in instruction_list:
                if giver == stakeholder_data[stakeholder]['id']:
                    ins, *args = ins.split('__')
                    cond, exp_action = self.instruction_function_map[ins]
                    if cond:
                        if action.value[0].__name__ == exp_action:
                            autonomy_utility = 1
                        else:
                            autonomy_utility = -1
                    else:
                        if action.value[0].__name__ != exp_action:
                            autonomy_utility = 1
                        else:
                            autonomy_utility = -1

            stakholder_autonomy_values.append((stakeholder, autonomy_utility))

        return stakholder_autonomy_values

    def get_wellbeing_utility(self, env, stakeholder_data, action, logger):
        """
        Calculating wellbeing utility values for stakeholders.

        wellbeing = 2/(1+e^((x-(m+n))(h(1-t))/2)) - 1

        x = time from last seen
        m = average time stay in
        n = std time stay in
        k = logistic growth rate = 1/2
        h = health (0<h<=1)
        t = history of emergencies = 1/(1+e^-kx) - x = number of emergencies of the past
        """


        # visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        #     center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        # visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]

        stakholder_wellbeing_values = []

        for stakeholder, data in stakeholder_data.items():
            if stakeholder == 'robot':
                continue

            wellbeing_util = 0

            if stakeholder == 'follower':
                # Simulating next pos and visible lines
                next_pos = action.value[0](*action.value[1:], act=False)
                follower_approx_next_pos = self.follower_nex_pos_approx(env, stakeholder_data, stakeholder)

                seen = stakeholder_data['robot']['model'].model.visibility_ab(next_pos, follower_approx_next_pos, ROBOT.VISIBLE_DIST)

                if action.value[0].__name__ == 'go_to_last_seen':
                    wellbeing_util = 0.5
                else:
                    if seen:
                        wellbeing_util = 1
                    else:
                        time = env['time']
                        e = np.finfo(float).eps
                        last_seen_time = data['last_seen_time']
                        x = time - last_seen_time
                        m, n = env['follower_avg_time_and_std_in_rooms'][data['last_seen_location']]
                        num_emer = env['no_of_follower_emergencies_in_past']
                        t = 1 / (1 + e ** (num_emer - 2))
                        h = env['follower_health_score']

                        wellbeing_util = 2 / (1 + e ** ((h * (1 - t)) * (x - (m + n)) / 2)) - 1

            else:
                wellbeing_util = 0

            stakholder_wellbeing_values.append((stakeholder, wellbeing_util))

        return stakholder_wellbeing_values

    def follower_nex_pos_approx(self, env, stakeholder_data, stakeholder):
        data = stakeholder_data[stakeholder]
        next_pos = tuple(map(lambda i, j: i + (i - j), data['pos'], (data['last_seen_pos'] if data['last_seen_pos'] else data['pos'])))

        if next_pos in env['walls']:
            next_pos = data['pos']

        return  next_pos
