import os

import ethical_governor.blackboard.evaluator.evaluator as evaluator


CASE_BASE = os.path.join(os.getcwd(), 'ethical_governor', 'blackboard', 'commonutils', 'cbr', 'case_base_gen_medication.json')

DUMP_query = False # Set to True to dump the query to a xlsx file. While this is true evaluator will not run as intended.



class PSRBEvaluator(evaluator.Evaluator):

    def __init__(self):
        super().__init__()
        
        cbr_context_data_feature_map = {
            'robot_location': ['stakeholders', 'robot', 'location'],
            'on_call': ['stakeholders', 'robot', 'on_call'],
            'caller_type': ['stakeholders', 'caller', 'type'],
            'caller_instruction': self.get_caller_instruction,
            'reciever_seen': self.get_receiver_seen,
            'receiver_location': self.get_receiver_location,
            'receiver_preference': self.get_receiver_preference,
            'receiver_with_company': self.get_with_company,
            'worker_seen': self.get_worker_seen,
            'worker_location': self.get_worker_location,
            'worker_preference': self.get_worker_preference,
            'other_patient_seen': self.get_other_patient_seen,
            'other_patient_locations': self.get_other_patient_locations,
            'other_negative_preference_%': self.get_other_negative_pref_percentage,
            'caller_autonomy': self.get_caller_autonomy,
            'reciever_wellbeing': self.get_receiver_wellbeing,
            'receiver_privacy': self.get_receiver_privacy,
            'worker_privacy': self.get_worker_privacy,
            'other_resident_privacy': self.get_other_patient_privacy # TODO: finish this method
        }

        # cbr_table_data_features = {
        #     'follower_autonomy': 'patient_0_autonomy', 'follower_wellbeing': 'patient_0_wellbeing', 'wellbeing_probability': 'patient_0_wellbeing_probability'
        # }

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        self.score = {}
        for action in data.get_actions():
            if data.get_table_data(action, 'is_breaking_rule'):
                self.score[action] = 0
            else:
                self.score[action] = 1
            logger.info('Desirability of action ' + str(action.value) + ' : ' + str(self.score[action]))


    def get_caller_instruction(self, action, data, logger):
        instruction_list = data.get_data('stakeholders', 'robot', 'instruction_list')
        for instruction in instruction_list:
            if instruction[1].type == 'caller':
                return instruction[0]
        return None
            

    def get_receiver_seen(self, action, data, logger):
        receiver = data.get_data('stakeholders', 'robot', 'receiver')
        for table_col in data.get_table_col_names():
            if receiver in table_col:
                return True
            
        return False
    

    def get_receiver_location(self, action, data, logger):
        if self.get_receiver_seen(action, data, logger):
            receiver = data.get_data('stakeholders', 'robot', 'receiver')
            location = data.get_data('stakeholders', receiver, 'seen_location')
            return location
        else:
            return None
    

    def get_receiver_preference(self, action, data, logger):
        if self.get_receiver_seen(action, data, logger):
            receiver = data.get_data('stakeholders', 'robot', 'receiver')
            preferences = data.get_data('stakeholders', receiver, 'preferences')
            
            location = data.get_data('stakeholders', receiver, 'seen_location')
            
            other_visible_stakeholders_ids = [stakeholder_id for stakeholder_id in data.get_data['stakeholders'].keys() if stakeholder_id not in ['robot', 'caller', receiver]]
            with_company = 'with_company' if len(other_visible_stakeholders_ids) > 0 else 'alone'
            
            
            preference = preferences[location]['receiver'][with_company]
            return preference
        else:
            return None
    

    def get_with_company(self, action, data, logger):
        if self.get_receiver_seen(action, data, logger):
            receiver = data.get_data('stakeholders', 'robot', 'receiver')
            other_visible_stakeholders_ids = [stakeholder_id for stakeholder_id in data.get_data['stakeholders'].keys() if stakeholder_id not in ['robot', 'caller', receiver]]
            with_company = 'with_company' if len(other_visible_stakeholders_ids) > 0 else 'alone'
            return with_company
        else:
            return None

    def get_worker_seen(self, action, data, logger):
        for id in data.get_data('stakeholders').keys():
            if id == 'care_worker':
                return True
        return False
    
    
    def get_worker_location(self, action, data, logger):
        if self.get_worker_seen(action, data, logger):
            return data.get_data('stakeholders', 'care_worker', 'seen_location')
        else:
            None

    def get_worker_preference(self, action, data, logger):
        if self.get_worker_seen(action, data, logger):
            preferences = data.get_data('stakeholders', 'care_worker', 'preferences')

            location = data.get_data('stakeholders', 'care_worker', 'seen_location')
            role = '3rd_party'

            other_visible_stakeholders_ids = [stakeholder_id for stakeholder_id in data.get_data['stakeholders'].keys() if stakeholder_id not in ['robot', 'caller', 'care_worker']]
            with_company = 'with_company' if len(other_visible_stakeholders_ids) > 0 else 'alone'

            preference = preferences[location][role][with_company]
            return preference
        else:
            return None
    
    def get_other_patient_seen(self, action, data, logger):
        stakeholder_data = data.get_data('stakeholders')
        for id in stakeholder_data.keys():
            if id not in ['robot', 'caller', stakeholder_data['robot']['receiver'], 'care_worker']:
                return True
        return False
    
    def get_other_patient_locations(self, action, data, logger):
        if self.get_other_patient_seen(action, data, logger):
            stakeholder_data = data.get_data('stakeholders')
            other_patient_locations = []
            for id in stakeholder_data.keys():
                if id not in ['robot', 'caller', data.get_data('stakeholders', 'robot', 'receiver'), 'care_worker']:
                    other_patient_locations.append(stakeholder_data[id]['seen_location'])
            return other_patient_locations
        else:
            return None
        
    def get_other_negative_pref_percentage(self, action, data, logger):
        if self.get_other_patient_seen(action, data, logger):
            other_patient_number = 0
            stakeholder_data = data.get_data('stakeholders')
            other_negative_pref_count = 0
            for id in stakeholder_data.keys():
                if id not in ['robot', 'caller', data.get_data('stakeholders', 'robot', 'receiver'), 'care_worker']:
                    preferences = stakeholder_data[id]['preferences']
                    location = stakeholder_data[id]['seen_location']
                    role = '3rd_party'
                    if len([stakeholder_id for stakeholder_id in stakeholder_data.keys() if stakeholder_id not in ['robot', 'caller', id]]) > 0:
                        with_company = 'with_company' 
                    else:
                        with_company = 'alone'
                    preference = preferences[location][role][with_company]
                    if not preference:
                        other_negative_pref_count += 1
                    other_patient_number += 1
            return other_negative_pref_count / other_patient_number
        else:
            return None
    
    def get_caller_autonomy(self, action, data, logger):
        return data.get_table_data(action, 'caller_autonomy')
    
    def get_receiver_wellbeing(self, action, data, logger):
        if self.get_receiver_seen(action, data, logger):
            receiver = data.get_data('stakeholders', 'caller', 'calling_resident')
            return data.get_table_data(action, receiver + '_wellbeing')
        else:
            return None

    def get_receiver_privacy(self, action, data, logger):
        if self.get_receiver_seen(action, data, logger):
            receiver = data.get_data('stakeholders', 'caller', 'calling_resident')
            return data.get_table_data(action, receiver + '_privacy')
        else:
            return None
    
    def get_worker_privacy(self, action, data, logger):
        if self.get_worker_seen(action, data, logger):
            return data.get_table_data(action, 'care_worker_privacy')
        else:
            return None
            
        