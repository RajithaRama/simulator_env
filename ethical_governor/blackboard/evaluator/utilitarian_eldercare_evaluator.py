import ethical_governor.blackboard.evaluator.evaluator as evaluator


class UtilitarianEvaluator(evaluator.Evaluator):

    def __init__(self):
        super().__init__()
        weight_dist = {'follower': 1, 'rest': 0.5}

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        for action in data.get_actions():
            desirability = 0
            follower_util = 0
            other_util = 0
            i = 0
            for stakeholder in data.get_stakeholders_data().keys():
                if stakeholder == 'robot':
                    continue

                if stakeholder == 'follower':
                    # Autonomy focused utilitarian agent
                    follower_util = (2 * data.get_table_data(action=action, column=stakeholder + '_autonomy') +
                                     data.get_table_data(action=action, column=stakeholder + '_wellbeing'))/3
                else:
                    i += 1
                    other_util += (data.get_table_data(action=action, column=stakeholder + '_autonomy') +
                                     data.get_table_data(action=action, column=stakeholder + '_wellbeing'))/2
            if other_util:
                other_util = other_util/i

            if other_util + follower_util > 0.5:
                desirability = 1
            elif other_util + follower_util < 0.2:
                desirability = 0
            else:
                desirability = other_util + follower_util

            logger.info('Desirability of action ' + str(action.value) + ' : ' + str(desirability))
            self.score[action] = desirability

