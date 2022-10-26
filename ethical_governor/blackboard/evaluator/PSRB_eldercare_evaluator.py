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




if __name__ == '__main__':
    ex1 = PSRBEvaluator()
    neighbours = ex1.expert_db.get_neighbours(pd.DataFrame(data=[[1, 'bedroom', 0, 'bedroom', 'bedroom', 0, [], 40, [], 'day', '0', '-1', '0', 'stay']], columns=['seen', 'follower_seen_location', 'follower_time_since_last_seen', 'last_seen_location', 'robot_location', 'not_follow_request', 'not_follow_locations', 'battery_level', 'instructions_given', 'time', 'follower_autonomy', 'follower_wellbeing', 'follower_availability', 'action']))
    print(neighbours)