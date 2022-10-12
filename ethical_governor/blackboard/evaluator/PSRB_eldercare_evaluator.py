import ethical_governor.blackboard.evaluator.evaluator as evaluator


class PSRBEvaluator(evaluator.Evaluator):
    def __init__(self):
        super().__init__()
        # self.expert_db = ExpertDB()

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        self.score = {}

