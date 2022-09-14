import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test


class ElderCareUtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        for action in data.get_actions():
            logger.info('Testing action: ' + str(action.value))

            logger.info('Calculating autonomy utility for stakeholders')
            autonomy_utility = self.get_autonomy_utility(data, action, logger)
            logger.info('Autonomy utilities for action ' + str(action.value) + ': ' + str(autonomy_utility))

    def get_autonomy_utility(self, data, action, logger):
        pass