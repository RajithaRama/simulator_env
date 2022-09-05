import blackboard.evaluator.evaluator as evaluator


class UtilitarianEvaluator(evaluator.Evaluator):

    def __init__(self):
        super().__init__()

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        for action in data.get_actions():
            desirability = 0
            if data.get_table_data(action, 'is_rule_broken'):
                desirability = data.get_table_data(action, "stakeholder_wellbeing") + data.get_table_data(action, 'social') + data.get_table_data(action, 'driver_autonomy')
            else:
                desirability = data.get_table_data(action, "stakeholder_wellbeing") + data.get_table_data(action, 'social') + 0.75 * data.get_table_data(action, 'driver_autonomy')
            logger.info('Desirability of action ' + str(action.value) + ' : ' + str(desirability))
            self.score[action] = desirability