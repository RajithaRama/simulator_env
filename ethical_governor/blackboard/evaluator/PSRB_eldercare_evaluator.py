import os
import pandas as pd

import ethical_governor.blackboard.evaluator.evaluator as evaluator
from ethical_governor.blackboard.commonutils.cbr.cbr import CBR

CASE_BASE = os.path.join(os.getcwd(), 'ethical_governor', 'blackboard', 'commonutils', 'cbr', 'casebase.json')

cbr_context_data_feature_map = {
    'seen': ['stakeholders', 'follower', 'seen'],
    'follower_seen_location': ['stakeholders', 'follower', 'seen_location'],
    'follower_time_since_last_seen': ['stakeholders', 'follower', 'last_seen_time'],
    'last_seen_location': ['stakeholders', 'follower', 'last_seen_location'],
    'robot_location': ['stakeholders', 'robot', 'location'],
    'not_follow_request': ['stakeholders', 'robot', 'not_follow_request'],
    'not_follow_locations': ['stakeholders', 'robot', 'not_follow_locations'],
    'battery_level': ['stakeholders', 'robot', 'battery_level'],
    'instructions_given': ['stakeholders', 'robot', 'instruction_list'],
    "time": ['environment', 'time_of_day']
}

cbr_table_data_features = ["follower_autonomy", "follower_wellbeing", "follower_availability", "action"]


class PSRBEvaluator(evaluator.Evaluator):
    def __init__(self):
        super().__init__()
        self.expert_db = CBR()
        with open(CASE_BASE) as fp:
            data_df = pd.read_json(CASE_BASE, orient='records')
            self.feature_list = self.expert_db.add_data(data_df)

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        self.score = {}

        for action in data.get_actions():
            expert_opinion = self.get_expert_opinion(action, data)
            logger.info('expert opinion on action ' + str(action) + ' : ' + str(expert_opinion))
            print(expert_opinion)

            if expert_opinion and not data.get_table_data(action=action, column='is_breaking_rule'):
                data.put_table_data(action=action, column='desirability_score', value=1)
            elif not expert_opinion and data.get_table_data(action=action, column='is_breaking_rule'):
                data.put_table_data(action=action, column='desirability_score', value=0)



    def get_expert_opinion(self, action, data):
        query = self.generate_query(action, data)
        print(query)

        neighbours_with_dist = self.expert_db.get_neighbours_with_distances(query=query)
        vote = self.expert_db.distance_weighted_vote(neighbours_with_dist=neighbours_with_dist, threshold=3)
        return vote

    def generate_query(self, action, data):
        query = pd.DataFrame()
        for feature in self.feature_list:
            if feature in ['case_id', 'acceptability']:
                continue
            if feature == 'action':
                query[feature] = [action]
                continue
            try:
                path = cbr_context_data_feature_map[feature]
            except KeyError:
                path = None
            if path:
                value = data.get_data(path)
            else:
                value = data.get_table_data(action=action, column=feature)

            query[feature] = [value]
        return query


if __name__ == '__main__':
    ex1 = PSRBEvaluator()
    neighbours = ex1.expert_db.get_neighbours_with_distances(
        pd.DataFrame(data=[[1, 'bedroom', 0, 'bedroom', 'bedroom', 0, [], 40, [], 'day', 0, -1, 0, 'stay']],
                     columns=['seen', 'follower_seen_location', 'follower_time_since_last_seen', 'last_seen_location',
                              'robot_location', 'not_follow_request', 'not_follow_locations', 'battery_level',
                              'instructions_given', 'time', 'follower_autonomy', 'follower_wellbeing',
                              'follower_availability', 'action']))
    print(neighbours)

    vote = ex1.expert_db.distance_weighted_vote(neighbours_with_dist=neighbours, threshold=3)
    print(vote)
