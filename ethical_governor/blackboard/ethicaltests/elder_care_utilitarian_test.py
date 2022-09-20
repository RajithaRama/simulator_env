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
            logger.info('Testing action: ' + str(action.value))

            logger.info('Calculating autonomy utility for stakeholders')
            autonomy_utility = self.get_autonomy_utility(env=env, stakeholder_data=stakeholder_data, action=action, logger=logger)
            logger.info('Autonomy utilities for action ' + str(action.value) + ': ' + str(autonomy_utility))

    def get_autonomy_utility(self, env, stakeholder_data, action, logger):

        # Simulating next pos and visible lines
        next_pos = action.value[0](*action.value[1:], act=False)
        # visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        # visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]
        robot_model = stakeholder_data['robot']['model']
        instruction_list = robot_model.model.get_commands(self)

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




            # autonomy_utility = 0
            # if robot_model.not_follow_request and (robot_model.follow == action.value[0]) and stakeholder == 'follower':
            #     autonomy_utility = -1
            # elif robot_model.not_follow_request and stakeholder == 'follower':
            #     autonomy_utility = 1
            #
            # if action.value[0] == robot_model.move_away:
            #     if stakeholder_data[stakeholder]['id'] == action.value[1]:
            #         autonomy_utility = 1
            #     else:
            #         auto


        return autonomy_utility