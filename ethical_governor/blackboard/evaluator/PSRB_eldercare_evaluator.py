import itertools
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
            data_df = pd.read_json(CASE_BASE, orient='records', precise_float=True)
            data_df[['follower_autonomy', 'follower_wellbeing', 'robot_availability']] = data_df[
                ['follower_autonomy', 'follower_wellbeing', 'robot_availability']].astype(float)
            self.feature_list = self.expert_db.add_data(data_df)

        self.charactor = {'wellbeing': 9, 'autonomy': 3, 'availability': 3}

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        self.score = {}

        for action in data.get_actions():
            logger.info('Evaluating action: ' + str(action))
            expert_opinion, expert_intention = self.get_expert_opinion(action, data, logger)
            logger.info('expert opinion on action ' + str(action) + ' : ' + str(expert_opinion) + ' with ' +
                        str(expert_intention) + ' intention')
            # print(expert_opinion)

            wellbeing = data.get_table_data(action=action, column='follower_wellbeing')
            autonomy = data.get_table_data(action=action, column='follower_autonomy')
            availability = data.get_table_data(action=action, column='robot_availability')

            # diff_wellbeing_autonomy = wellbeing - autonomy
            # diff_wellbeing_availability = wellbeing - availability
            # diff_autonomy_availability = autonomy - availability

            rule_broken = data.get_table_data(action=action, column='is_breaking_rule')
            if expert_opinion and not rule_broken:
                # When rules and expert both accept
                data.put_table_data(action=action, column='desirability_score', value=1)
                logger.info("Action " + action.value[0].__name__ + ' desirability: 1' + '| Reason: no rules broken and '
                                                                                       'accepted by experts.')
            elif not expert_opinion and rule_broken:
                # When rules and expert reject
                data.put_table_data(action=action, column='desirability_score', value=0)
                logger.info("Action " + action.value[0].__name__ + ' desirability: 0' + '| Reason: rules ' + str(
                    data.get_table_data(action=action, column='breaking_rule_ids')) + ' broken and not '
                                                                                      'accepted by experts.')
            elif expert_opinion and rule_broken:
                # when rules reject but experts accept
                values = self.charactor.keys()

                acceptability = 1
                for value in values:
                    if value in expert_intention:
                        threshold = (10 - self.charactor[value]) / 10
                        if eval(value) < threshold:
                            acceptability = 0
                    else:
                        threshold = (self.charactor[value] - 10) / 10
                        if eval(value) < threshold:
                            acceptability = 0
                data.put_table_data(action=action, column='desirability_score', value=acceptability)

                if acceptability:
                    logger.info("Action " + action.value[0].__name__ + ' desirability: 1' + '| Reason: rules ' + str(
                        data.get_table_data(action=action, column='breaking_rule_ids')) + 'broken, but accepted by '
                                                                                          'experts. Since it increases ' + str(expert_intention) + 'values greatly, deemed accepted by PSRB '
                                                                                                                                              'system.')
                else:
                    logger.info("Action " + action.value[0].__name__ + ' desirability: 0' + '| Reason: rules ' + str(
                        data.get_table_data(action=action, column='breaking_rule_ids')) + 'broken, but accepted by '
                        'experts. However, the value tradeoff is not satisfactory to bend the rule.')
            else:
                # When rules accept and experts reject
                acceptability = 1
                for value in expert_intention:
                    lower_threshold = (self.charactor[value] - 10) / 10
                    if eval(value) < lower_threshold:
                        acceptability = 0
                data.put_table_data(action=action, column='desirability_score', value=acceptability)

                if acceptability:
                    logger.info("Action " + action.value[0].__name__ + ' desirability: 1' + '| Reason: no rules broken, but not accepted by '
                        'experts. However, PSRB system suggest the value tradeoff not enough to bend the rule.')

                else:
                    logger.info("Action " + action.value[0].__name__ + ' desirability: 0 | Reason: no rules broken, but not accepted by '
                        'experts. Since it decreases ' + str(expert_intention) + 'values too much, deemed not accepted by '
                                                                                                                       'PSRB system.')

                # for item1, item2 in itertools.combinations(self.charactor.keys(), 2):
                #     if eval(item1) == eval(item2)
                #     if item1(eval(item1)-eval(item2))/abs(eval(item1)-eval(item2)) == (self.charactor[item1] - self.charactor[
                #         item2]) / abs((self.charactor[item1] - self.charactor[item2])):

    def get_expert_opinion(self, action, data, logger):
        query = self.generate_query(action, data)
        # print(query)

        neighbours_with_dist = self.expert_db.get_neighbours_with_distances(query=query, logger=logger)
        logger.info('closest neighbours to the case are: ' + str(neighbours_with_dist))
        vote, intention = self.expert_db.distance_weighted_vote(neighbours_with_dist=neighbours_with_dist, threshold=3,
                                                                logger=logger)

        return vote, intention

    def generate_query(self, action, data):
        query = pd.DataFrame()
        for feature in self.feature_list:
            if feature in ['case_id', 'acceptability', 'intention']:
                continue
            if feature == 'action':
                query[feature] = [action.value[0].__name__]
                continue
            try:
                path = cbr_context_data_feature_map[feature]
            except KeyError:
                path = None
            if path:
                if feature == "follower_time_since_last_seen":
                    last_seen_time = data.get_data(path) if data.get_data(path) is not None else 0
                    value = last_seen_time - data.get_data(['environment', 'time'])
                else:
                    value = data.get_data(path)
            else:
                value = data.get_table_data(action=action, column=feature)

            if value == None:
                continue
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
    # print(neighbours)

    vote = ex1.expert_db.distance_weighted_vote(neighbours_with_dist=neighbours, threshold=3)
    # print(vote)
