import os
import pandas as pd

import ethical_governor.blackboard.evaluator.evaluator as evaluator
from ethical_governor.blackboard.commonutils.cbr.cbr import CBR

CASE_BASE = os.path.join(os.getcwd(), 'ethical_governor', 'blackboard', 'commonutils', 'cbr', 'casebase')


class PSRBEvaluator(evaluator.Evaluator):
    def __init__(self):
        super().__init__()
        self.expert_db = CBR()
        data_df = pd.read_csv(CASE_BASE)
        self.expert_db.add_data(data_df)

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        self.score = {}
