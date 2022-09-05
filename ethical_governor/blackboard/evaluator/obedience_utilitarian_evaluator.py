import blackboard.evaluator.evaluator as evaluator


class UtilitarianEvaluator(evaluator.Evaluator):

    def __init__(self):
        super().__init__()

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        for action in data.get_actions():
            desirability = 0
            if data.get_table_data(action, "user_safety") == 0:
                desirability = data.get_table_data(action, "obedience") + 0.75 * data.get_table_data(action,
                                                                                                     "robot_safety")
            else:
                desirability = 2 * data.get_table_data(action, "user_safety") + 0.75 * (data.get_table_data(action,
                                                                                                           "robot_safety") + data.get_table_data(action, "obedience"))
            logger.info('Desirability of action ' + str(action.value) + ' : ' + str(desirability))
            self.score[action] = desirability

