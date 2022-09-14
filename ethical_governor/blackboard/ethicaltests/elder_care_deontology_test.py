import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test
import yaml
import os

dirname = os.path.dirname(__file__)


def load_yaml(input_yaml):
    with open(input_yaml, 'r') as fp:
        yaml_data = yaml.load(fp, Loader=yaml.FullLoader)
    return yaml_data


class ElderCareRuleTest(ethical_test.EthicalTest):
    class rule:
        condition = None
        permissibility = None

        operations = {'<': lambda left, right: left < right,
                      '>': lambda left, right: left > right,
                      'and': lambda left, right: left and right,
                      'or': lambda left, right: left or right,
                      '==': lambda left, right: left == right,
                      'in': lambda left, right: left in right}

        def read_formula(self, formula_str):
            formula = []
            tokens = self.token_generator(formula_str)
            formula = self.populate_formula(tokens, formula)
            # print(formula)
            return formula

        def populate_formula(self, tokens, list):
            for token in tokens:
                if token == ')':
                    return list
                elif token == '(':
                    new_list = []
                    new_list = self.populate_formula(tokens, new_list)
                    list.append(new_list)
                else:
                    list.append(token)
            return list

        def token_generator(self, formula_str):
            for item in formula_str.split():
                yield item

        def __init__(self, variables, condition, permissibility):
            self.variables = variables
            self.condition = self.read_formula(condition)
            self.permissibility = permissibility

        def get_condition(self):
            return self.condition

        def get_permissibility(self, data, action):
            if self.check_condition(data, action):
                return self.permissibility
            return None

        def check_condition(self, data, action):
            if self.solve(data=data, action=action, token_list=self.condition):
                return True
            else:
                return False

        def solve(self, data, action, token_list):
            left = None
            operation = None
            right = None
            for item in token_list:
                # if list solve it and assign
                if type(item) == list:
                    if (left is not None) and operation:
                        right = self.solve(data=data, token_list=item, action=action)
                    elif operation and left is None:
                        raise ValueError("Error in rule input")
                    else:
                        left = self.solve(data=data, token_list=item, action=action)
                # if variable find it and assign
                elif item in self.variables:
                    path = item.split('.')
                    value = {'environment': data.get_environment_data(), 'stakeholders': data.get_stakeholders_data(),
                             'action': action}
                    for i in path:
                        value = value[i]

                    if left and operation:
                        right = value
                    elif operation and not left:
                        raise ValueError("Error in rule input")
                    else:
                        left = value
                # if it's an operation, assign
                elif item in self.operations.keys():
                    operation = item
                # if it is a constant numeral, assign as a float
                elif item.isnumeric():
                    value = float(item)
                    if left and operation:
                        right = value
                    elif operation and not left:
                        raise ValueError("Error in rule input")
                    else:
                        left = value
                # else treat is as a string
                else:
                    if left and operation:
                        right = item
                    elif operation and not left:
                        raise ValueError("Error in rule input")
                    else:
                        left = item
                # solve, assign to left
                if (left is not None) and (right is not None) and (operation is not None):
                    left = self.operations[operation](left, right)
                    operation = right = None
            if operation or (right is not None):
                ValueError("Incomplete rule condition")
            return left

    def __init__(self, test_data):
        super().__init__(test_data)
        self.rule_file = test_data['other']['rule_file']
        self.rules = {}
        for id, variables, condition, perm in load_yaml(os.path.join(dirname, "./conf/" + self.rule_file)):
            # print(id, variables, condition, perm)
            self.rules[id] = self.rule(variables, condition, perm)

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        for action in data.get_actions():
            logger.info('Testing action: ' + str(action.value[0]))
            permissible = True
            ids_of_broken_rules = []
            # TODO: Check log
            for id, rule in self.rules.items():
                if rule.get_permissibility(data, action.value[0].__name__) == False:
                    permissible = False
                    ids_of_broken_rules.append(id)

            if permissible:
                logger.info('Action ' + str(action) + ' : Permissible')
            else:
                logger.info('Action ' + str(action) + ' : Not permissible since it broke rules ' + str(ids_of_broken_rules))

            self.output[action] = {'is_breaking_rule': not permissible, 'breaking_rule_ids': ids_of_broken_rules}

        logger.info(__name__ + ' finished.')
