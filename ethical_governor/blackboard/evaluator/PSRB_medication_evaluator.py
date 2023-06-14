import os
import pandas as pd
import ethical_governor.blackboard.evaluator.evaluator as evaluator
from Models.home_medication import MedImpact

from ethical_governor.blackboard.commonutils.cbr.cbr_medication import CBRMedication

CASE_BASE = os.path.join(os.getcwd(), 'ethical_governor', 'blackboard', 'commonutils', 'cbr', 'case_base_gen_medication.json')

DUMP_query = False # Set to True to dump the query to a xlsx file. While this is true evaluator will not run as intended.

cbr_context_data_feature_map = {
    'took_meds': ['stakeholders', 'patient_0', 'took_meds'],
    'med_name': ['stakeholders', 'patient_0', 'attached_reminders', 'med_name'],
    'med_type': ['environment', 'Medication_info', ['stakeholders', 'patient_0', 'attached_reminders', 'med_name'], 'type'],
    'med_impact': ['environment', 'Medication_info', ['stakeholders', 'patient_0', 'attached_reminders', 'med_name'], 'impact'],
    'time_since_last_reminder': ['stakeholders', 'patient_0', 'attached_reminders', 'time'],
    'state': ['stakeholders', 'patient_0', 'attached_reminders', 'state'],
    'no_of_missed_doses':['stakeholders', 'patient_0', 'no_of_missed_doses'],
    'no_of_followups':['stakeholders', 'patient_0', 'attached_reminders', 'no_of_followups'],
    'no_of_snoozes': ['stakeholders', 'patient_0', 'attached_reminders', 'no_of_snoozes'],
    'user_response': ['stakeholders', 'robot', 'instruction_list', 0, 0],
    'time_of_day': ['environment', 'time_of_day']
}

cbr_table_data_features = {
    'follower_autonomy': 'patient_0_autonomy', 'follower_wellbeing': 'patient_0_wellbeing', 'wellbeing_probability': 'patient_0_wellbeing_probability'
}

class PSRBEvaluator(evaluator.Evaluator):

    def __init__(self):
        super().__init__()
        self.expert_db = CBRMedication()
        with open(CASE_BASE) as fp:
            data_df = pd.read_json(CASE_BASE, orient='records', precise_float=False)
            data_df[['follower_autonomy', 'follower_wellbeing', 'wellbeing_probability']] = data_df[['follower_autonomy', 'follower_wellbeing', 'wellbeing_probability']].astype(float)
            self.feature_list = self.expert_db.add_data(data_df)

        if DUMP_query:
            self.queries = pd.DataFrame(columns=self.feature_list)

        self.charactor = {'wellbeing': 9, 'autonomy': 3, 'risk_propensity': 3}

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        self.score = {}
        # for action in data.get_actions():
        #     if data.get_table_data(action, 'is_breaking_rule'):
        #         self.score[action] = 0
        #     else:
        #         self.score[action] = 1
        #     logger.info('Desirability of action ' + str(action.value) + ' : ' + str(self.score[action]))


        for action in data.get_actions():
            logger.info('Evaluating action: ' + str(action))
            expert_opinion, expert_intention = self.get_expert_opinion(action, data, logger)
            # logger.info('expert opinion on action ' + str(action) + ' : ' + str(expert_opinion) + ' with ' +
                        # str(expert_intention) + ' intention')
            
            # TODO: Rest of the algorithm
            data.put_table_data(action=action, column='desirability_score', value=1)
            

    
    def get_expert_opinion(self, action, data, logger):
        query = self.generate_query(action, data)
        # print(query)
        if DUMP_query:
            self.dump_query(query)
            vote = 1
            intention = 'test'
        else:
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
                if feature == "time_since_last_reminder":
                    if data.get_data(path) is not None:
                        last_remind_time = data.get_data(path)
                        value = data.get_data(['environment', 'time']) - last_remind_time
                    else:
                        value = None
                elif feature == "took_meds":
                    if data.get_data(path) == True:
                        value = 1
                    else:
                        value = 0
                elif feature == "med_impact" and type(data.get_data(path)) == MedImpact:
                    value = data.get_data(path).value
                else:
                    value = data.get_data(path)
            else:
                path = cbr_table_data_features[feature]
                value = data.get_table_data(action=action, column=path)

            if value == None:
                if DUMP_query:
                    query[feature] = [value]
                continue

            query[feature] = [value]
            
        return query
    
    def dump_query(self, query):
        
        self.queries = self.queries.append(query, ignore_index=True)
        self.queries.to_excel('query_dump.xlsx', sheet_name='query')