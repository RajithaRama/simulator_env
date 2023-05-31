import numpy as np

import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test
import agent_types.medication_robot as ROBOT


class MedicationUtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)
        self.instruction_function_map = {
            'SNOOZE': [True, ROBOT.Robot.snooze.__name__],
            'ACKNOWLEDGE': [True, ROBOT.Robot.acknowledge.__nam//.e__]
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
        """

        # visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        #     center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        # visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]

        stakholder_wellbeing_values = []

        for stakeholder, data in stakeholder_data.items():
            if stakeholder == 'robot':
                continue

            wellbeing_util = 0.0

            if stakeholder == 'follower':
                # TODO: Implement follower wellbeing utility
                pass

            stakholder_wellbeing_values.append((stakeholder, wellbeing_util))

        return stakholder_wellbeing_values

