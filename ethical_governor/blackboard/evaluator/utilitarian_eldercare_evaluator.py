import ethical_governor.blackboard.evaluator.evaluator as evaluator


class UtilitarianEvaluator(evaluator.Evaluator):

    def __init__(self):
        super().__init__()
        weight_dist = {'follower': 1, 'rest': 0.5}

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        for action in data.get_actions():
            desirability = 0
            i = 0
            for stakeholder in data.get_stakeholders_data().keys():
                i += 1
                if data.get_table_data(action, stakeholder + "_Wellbeing") == 0:
                    desirability += data.get_table_data(action, stakeholder + "_Autonomy")
                else:
                    desirability += 2 * data.get_table_data(action, "Wellbeing") + 0.75 * (data.get_table_data(action,
                                                                                                               "Autonomy") + data.get_table_data(action, "obedience"))
            logger.info('Desirability of action ' + str(action.value) + ' : ' + str(desirability))
            self.score[action] = desirability

