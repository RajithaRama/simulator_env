import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test
import agent_types.robot as ROBOT


class ElderCareUtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)

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
        next_pos = action.value[0](*action.value[1:], act=False)
        visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)

        autonomy_utility = 0
        # if
        return autonomy_utility