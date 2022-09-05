import pandas as pd
import yaml

pd.set_option("display.max_rows", None, "display.max_columns", None)


def load_yaml(input_yaml):
    with open(input_yaml, 'r') as fp:
        yaml_data = yaml.load(fp, Loader=yaml.FullLoader)
    return yaml_data


class Data:

    def __init__(self, data_input, conf):
        self._environment = data_input['Environment']
        self._actions = [Action(i) for i in data_input['Suggested_actions']]
        self._stakeholders = data_input['Stakeholders']

        self._other_inputs = data_input['Other_inputs']

        columns = []
        for key in conf["tests"].keys():
            columns.append(conf["tests"][key]["output_names"])
        columns = [item for sublist in columns for item in sublist]
        columns.append('desirability_score')

        self._table_df = pd.DataFrame(columns=columns, index=self._actions)
        # print(self._table_df)

    def get_environment_data(self):
        return self._environment

    def get_actions(self):
        return self._actions

    def get_stakeholders_data(self):
        return self._stakeholders

    def get_table_data(self, action, column):
        return self._table_df.loc[action, column]

    def get_other_inputs(self):
        return self._other_inputs

    def put_table_data(self, action, column, value):
        self._table_df.loc[action, column] = value

    def get_max_index(self, column):
        column_value = self._table_df[column]
        return column_value[column_value == column_value.max()].index.to_list()

    def log_table(self, logger):
        logger.info('\n' + str(self._table_df))


class Action:
    def __init__(self, action):
        self.value = action

    def __str__(self):
        return "{}".format(self.value)
