import os
import ethical_governor.blackboard.evaluator.evaluator as evaluator

from ethical_governor.blackboard.commonutils.cbr.cbr import CBR

CASE_BASE = os.path.join(os.getcwd(), 'ethical_governor', 'blackboard', 'commonutils', 'cbr', 'case_base_gen.json')


cbr_context_data_feature_map = {
    'took_meds': ['stakeholders', 'patient_0', 'took_meds'],
    'med_name': ['stakeholders', 'patient_0', 'attached_reminders', 'med_name'],
    'med_type': ['environment', 'Medication_info', ['stakeholders', 'patient_0', 'attached_reminders', 'med_name'], 'type']
}
#TODO: when traversing algorithm found a list, it should go to the location and get data and use that in the given step


class PSRBEvaluator(evaluator.Evaluator):

    

    def __init__(self):
        super().__init__()

    def evaluate(self, data, logger):
        logger.info(__name__ + ' started evaluation using the data in the blackboard.')
        self.score = {}
        for action in data.get_actions():
            if data.get_table_data(action, 'is_breaking_rule'):
                self.score[action] = 0
            else:
                self.score[action] = 1
            logger.info('Desirability of action ' + str(action.value) + ' : ' + str(self.score[action]))
