import numpy as np

import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test
import agent_types.medication_robot as ROBOT


class MedicationUtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)
        self.instruction_function_map = {
            'SNOOZE': [True, ROBOT.Robot.snooze.__name__],
            'ACKNOWLEDGE': [True, ROBOT.Robot.acknowledge.__name__]
        }

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        env = data.get_environment_data()
        stakeholder_data = data.get_stakeholders_data()

        for action in data.get_actions():
            utils = {}

            logger.info('Testing action: ' + str(action.value))

            # logger.info('Calculating autonomy utility for stakeholders')
            autonomy_utility = self.get_autonomy_utility(env=env, stakeholder_data=stakeholder_data, action=action,
                                                         logger=logger)
            # logger.info('Autonomy utilities for action ' + str(action.value) + ': ' + str(autonomy_utility))
            utils['autonomy'] = autonomy_utility

            # logger.info('Calculating well-being utility for stakeholders')
            wellbeing_util = self.get_wellbeing_utility(env=env, stakeholder_data=stakeholder_data, action=action,
                                                        logger=logger)
            # logger.info('Wellbeing utilities for action ' + str(action.value) + ': ' + str(wellbeing_util))
            utils['wellbeing'] = wellbeing_util

            out = {}
            for util_type, values in utils.items():
                if util_type == 'wellbeing':
                    for stakeholder, util_value, probability in values:
                        col_name_util = stakeholder + '_' + util_type
                        col_name_prob = stakeholder + '_' + 'wellbeing_probability'
                        out[col_name_util] = util_value
                        out[col_name_prob] = probability
                else:
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

        instruction_list = stakeholder_data['robot']['instruction_list']

        stakholder_autonomy_values = []

        for stakeholder, data in stakeholder_data.items():
            # skip for robot
            if stakeholder == 'robot':
                continue

            autonomy_utility = 0.0

            if data['attached_reminders']:
                for instruction in instruction_list:
                    if instruction[1].id == stakeholder_data[stakeholder]['id']:
                        if self.instruction_function_map[instruction[0]] == action.value[0].__name__:
                            autonomy_utility = 1.0
                        else:
                            autonomy_utility = -1.0

                if action.value[0].__name__ == 'followup':
                    autonomy_utility = -0.5
                elif action.value[0].__name__ == 'record':
                    autonomy_utility = 0.5
                elif action.value[0].__name__ == 'record_and_call_careworker':
                    autonomy_utility = -1.0

            stakholder_autonomy_values.append((stakeholder, autonomy_utility))

        return stakholder_autonomy_values

    def get_wellbeing_utility(self, env, stakeholder_data, action, logger):
        """
        variables:
        - e_m = effect of the medication
        - d_m = Number of continuously missing doses

        utility = 1 / (e^( (a+b*d_m)*e_m )) -1)

        y\ =\frac{g}{\sqrt{2\pi}}\exp\left(-g\left(x+b\right)^{2}\right)

        """

        # visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        #     center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        # visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]

        stakholder_wellbeing_values = []

        for stakeholder, data in stakeholder_data.items():
            if stakeholder == 'robot':
                continue

            wellbeing_util = 0.0
            proba = 1.0

            if data['attached_reminders']:

                e_m = env['environment']['Medication_info'][data['attached_reminders']['med_name']]['impact'].value
                d_m = data['attached_reminders']['timer'].no_of_missed_doses

                if data['attached_reminders']['state'] == ROBOT.ReminderState.ISSUED:
                    d_m += (env['time'] - data['attached_reminders']['time']) / 8
                    utility, probability = self.highest_probable_utility(e_m, d_m)
                    if not action.value[0].__name__ == 'acknowledge':
                        wellbeing_util = utility
                        proba = probability

                elif data['attached_reminders']['state'] == ROBOT.ReminderState.SNOOZED:
                    d_m += data['attached_reminders']['no_of_snoozes'] / 3
                    utility, probability = self.highest_probable_utility(e_m, d_m)
                    wellbeing_util = utility
                    proba = probability

                elif data['attached_reminders']['state'] == ROBOT.ReminderState.ACKNOWLEDGED:
                    if not data['took_meds']:
                        if action.value[0].__name__ == 'followup':
                            d_m += data['attached_reminders']['no_of_followups'] / 4
                            wellbeing_util, proba = self.highest_probable_utility(e_m, d_m)
                        elif action.value[0].__name__ == 'record':
                            d_m += 1
                            wellbeing_util, proba = self.highest_probable_utility(e_m, d_m)
                        elif action.value[0].__name__ == 'record_and_call_careworker':
                            wellbeing_util = 0.5
                            proba = 1.0

                # TODO: Finish calculating the follower wellbeing utility
            else:
                if action.value[0].__name__ == 'remind_medication' and action.value[1].recipient == stakeholder:
                    wellbeing_util = 1.0

            stakholder_wellbeing_values.append((stakeholder, wellbeing_util, proba))

        return stakholder_wellbeing_values

    def highest_probable_utility(self, e_m, d_m):
        "Calculate the highest probable utility of the stakeholder"

        x, y = self.Utility_dist(e_m, d_m)
        max_prob = np.max(y)
        utility = np.where(y == max_prob)

        max_prob = max_prob if max_prob < 1 else 1

        return utility, max_prob

    def Utility_dist(self, e_m, d_m):
        """Generate a probability distribution of the utility of stakeholder
        """

        d = d_m
        f = e_m
        b = 1 - np.exp(-1 * (d + f - 1.5))
        g = (f / 2) * np.log(2 * d + 1)

        x = np.linspace(-1, 0, 100)

        y = (g / 2 * np.pi) * np.exp(-g * (x + b) ** 2)

        return x, y
