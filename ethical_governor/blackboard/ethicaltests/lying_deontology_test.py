# TO-DO
import blackboard.ethicaltests.ethical_test as ethical_test
import yaml
import os

dirname = os.path.dirname(__file__)


def load_yaml(input_yaml):
    with open(input_yaml, 'r') as fp:
        yaml_data = yaml.load(fp, Loader=yaml.FullLoader)
    return yaml_data


class ActDeontologyTest(ethical_test.EthicalTest):
    class rule:
        action = None
        permissibility = None

        def __init__(self, action, permissibility):
            self.action = action
            self.permissibility = permissibility

        def get_action(self):
            return self.action

        def get_permissibility(self):
            return self.permissibility

    def __init__(self, test_data):
        super().__init__(test_data)
        self.rules = {}
        for id, action, perm in load_yaml(os.path.join(dirname, "./conf/act_deontology_rules.yaml")):
            self.rules[id] = self.rule(action, perm)

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        for action in data.get_actions():
            logger.info('Testing action: ' + action.value)
            permissible = True
            ids_of_broken_rules = []
            for id, rule in self.rules.items():
                if action.value != rule.get_action():
                    continue
                elif rule.get_permissibility() < 0:
                    permissible = False
                    ids_of_broken_rules.append(id)

            if permissible:
                logger.info('Action "' + action.value + '" : Permissible')
            else:
                logger.info('Action "' + action.value + '" : Not permissible since it broke rule(s) ' + str(ids_of_broken_rules))

            self.output[action] = {self.output_names[0]: not permissible, self.output_names[1]: ids_of_broken_rules}