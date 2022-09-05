import blackboard.ethicaltests.ethical_test as ethical_test
import yaml
import os

dirname = os.path.dirname(__file__)


def load_yaml(input_yaml):
    with open(input_yaml, 'r') as fp:
        yaml_data = yaml.load(fp, Loader=yaml.FullLoader)
    return yaml_data


class RoadRuleTest(ethical_test.EthicalTest):
    class rule:
        condition = None
        permissibility = None

        operations = {'<': lambda left, right: left < right,
                      '>': lambda left, right: left > right,
                      'and': lambda left, right: left and right,
                      'or': lambda left, right: left or right,
                      '==': lambda left, right: left == right}

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

        def get_permissibility(self, data):
            if self.check_condition(data):
                return self.permissibility
            return None

        def check_condition(self, data):
            if self.solve(data, self.condition):
                return True
            else:
                return False

        def solve(self, data, token_list):
            left = None
            operation = None
            right = None
            for item in token_list:
                # if list solve it and assign
                if type(item) == list:
                    if left and operation:
                        right = self.solve(data, item)
                    elif operation and left is None:
                        raise ValueError("Error in rule input")
                    else:
                        left = self.solve(data, item)
                # if variable find it and assign
                elif item in self.variables:
                    path = item.split('.')
                    value = {'Environment': data.get_environment_data(), 'Stakeholders': data.get_stakeholders_data()}
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
        self.rules = {}
        for id, variables, condition, perm in load_yaml(os.path.join(dirname, "./conf/road_rules.yaml")):
            # print(id, variables, condition, perm)
            self.rules[id] = self.rule(variables, condition, perm)

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        for action in data.get_actions():
            logger.info('Testing action: ' + action.value)
            permissible = True
            ids_of_broken_rules = []
            if action.value == 'take_control':
                permissible = True
                # self.output[action] = {self.output_names[0]: False, self.output_names[1]: []}
                # logger.info('')
            else:
                for id, rule in self.rules.items():
                    if not rule.get_permissibility(data):
                        permissible = False
                        ids_of_broken_rules.append(id)
            if permissible:
                logger.info('Action "' + action.value + '" : Permissible')
            else:
                logger.info('Action "' + action.value + '" : Not permissible since it broke rules ' + str(ids_of_broken_rules))

            self.output[action] = {self.output_names[0]: not permissible, self.output_names[1]: ids_of_broken_rules}

        logger.info(__name__ + ' finished.')
