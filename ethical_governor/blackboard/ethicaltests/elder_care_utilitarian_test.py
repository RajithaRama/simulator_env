import numpy as np

import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test
import agent_types.robot as ROBOT


class ElderCareUtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)
        self.instruction_function_map = {
            'do_not_follow_to': [False, ROBOT.Robot.follow.__name__],
            'continue': [True, ROBOT.Robot.follow.__name__],
            'move_away': [True, ROBOT.Robot.move_away.__name__]
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

            logger.info('Calculating the availability for stakeholders')
            availability_util = self.get_availability_util(env=env, stakeholder_data=stakeholder_data, action=action,
                                                           logger=logger)
            logger.info('Availability utils for action ' + str(action.value) + ': ' + str(availability_util))
            utils['availability'] = availability_util

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
        # next_pos = action.value[0](*action.value[1:], act=False)
        # visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        # center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        # visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]
        instruction_list = stakeholder_data['robot']['instruction_list']

        stakholder_autonomy_values = []

        for stakeholder in stakeholder_data.keys():
            # skip for robot
            if stakeholder == 'robot':
                continue

            autonomy_utility = 0

            if stakeholder == 'follower' and stakeholder_data['robot']['model'].not_follow_request and \
                    action.value[0].__name__ == self.instruction_function_map['do_not_follow_to'][1]:
                if self.instruction_function_map['do_not_follow_to'][0]:
                    autonomy_utility = 1
                else:
                    autonomy_utility = -1

                if stakeholder_data['robot']['location'] in stakeholder_data['robot']['not_follow_locations']:
                    autonomy_utility = -1

            for ins, giver in instruction_list:
                if giver.id == stakeholder_data[stakeholder]['id']:
                    ins, *args = ins.split('__')
                    cond, exp_action = self.instruction_function_map[ins]
                    # if it is a positive request (i.e. asking to do something) then not doing it is -1 and doing it is
                    # 1. But if it is a negative request (i.e. asking not to do something), thn doing that is -1, but
                    # doing everything else is neutral (0).
                    if cond:
                        if action.value[0].__name__ == exp_action:
                            autonomy_utility = 1
                        else:
                            autonomy_utility = -1
                    else:
                        if action.value[0].__name__ == exp_action:
                            autonomy_utility = -1

            # if stakeholder == 'follower' and stakeholder_data['robot']['model'].not_follow_request and \
            #         action.value[0].__name__ == self.instruction_function_map['do_not_follow_to'][1]:
            #     autonomy_utility = 1

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

                seen = False
                if data['seen']:
                    follower_approx_next_pos = self.follower_nex_pos_approx(env, stakeholder_data, stakeholder)
                    seen = stakeholder_data['robot']['model'].model.visibility_ab(next_pos, follower_approx_next_pos,
                                                                                  ROBOT.VISIBLE_DIST)

                if seen:
                    wellbeing_util = 1
                else:
                    time = env['time']
                    last_seen_time = data['last_seen_time']
                    x = time - last_seen_time
                    m, n = env['follower_avg_time_and_std_in_rooms'][data['last_seen_location']]
                    num_emer = env['no_of_follower_emergencies_in_past']
                    t = 1 / (1 + np.exp(num_emer - 2))
                    h = env['follower_health_score']

                    wellbeing_util = 2 / (1 + np.exp(((h * (1 - t)) * (x - (m + n)) / 2))) - 1

                if action.value[0].__name__ == 'go_to_last_seen':
                    if wellbeing_util < 0:
                        wellbeing_util = -wellbeing_util
                    if wellbeing_util < 0.5:
                        wellbeing_util = wellbeing_util * 1.5
                    elif wellbeing_util < 0.8:
                        wellbeing_util = wellbeing_util + 0.2

            else:
                wellbeing_util = 0

            stakholder_wellbeing_values.append((stakeholder, wellbeing_util))

        return stakholder_wellbeing_values

    def follower_nex_pos_approx(self, env, stakeholder_data, stakeholder):
        data = stakeholder_data[stakeholder]
        if data['seen']:
            next_pos = tuple(map(lambda i, j: i + (i - j), data['pos'],
                                 (data['last_seen_pos'] if data['last_seen_pos'] else data['pos'])))
        else:
            next_pos = data['last_seen_pos']

        if next_pos in env['walls']:
            next_pos = data['pos']

        return next_pos

    def get_availability_util(self, env, stakeholder_data, action, logger):
        # TODO: implement

        battery_level = stakeholder_data['robot']['battery_level']
        availability = (-2 / (battery_level + 1)) + 1.02

        if action.value[0].__name__ == 'go_to_charge_station':
            availability = availability * 2 if availability < 0.4 else availability

        stakeholder_availability_values = [('robot', availability)]

        return stakeholder_availability_values
