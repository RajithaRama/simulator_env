import blackboard.ethicaltests.ethical_test as ethical_test


class UtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        for action in data.get_actions():
            logger.info('Testing action: ' + action.value)

            logger.info('Calculating social behaviour utility ')
            social_utility = self.get_social_behaviour_utility(data, action, logger)
            logger.info('Social utility for action ' + str(action.value) + ': ' + str(social_utility))

            logger.info('Calculating stakeholder wellbeing utility')
            stakeholder_wellbeing = self.get_stakeholder_wellbeing_utility(data, action, logger)
            logger.info(
                'Stakeholder wellbeing utility for action ' + str(action.value) + ': ' + str(stakeholder_wellbeing))

            logger.info('Calculating user autonomy utility')
            autonomy = self.get_driver_autonomy_utility(data, action, logger)
            logger.info('User autonomy utility for action ' + str(action.value) + ': ' + str(autonomy))

            self.output[action] = {self.output_names[0]: social_utility, self.output_names[1]: stakeholder_wellbeing,
                                   self.output_names[2]: autonomy}
        logger.info(__name__ + ' finished.')

    def get_social_behaviour_utility(self, data, action, logger):
        if action.value == 'take_control':
            return 1
        driver_data = self.get_driver(data)
        logger.info("Getting rule breaking info for action " + str(action.value) + " from the table.")
        if data.get_table_data(action, 'is_rule_broken') and not driver_data[1]:
            return -1
        elif data.get_table_data(action, 'is_rule_broken') and driver_data[1]:
            return -0.5
        else:
            return 1

    def get_stakeholder_wellbeing_utility(self, data, action, logger):
        envir_data = data.get_environment_data()
        diff_speed = (envir_data['vehicle_speed'] - envir_data['speed_limit']) if (
                envir_data['vehicle_speed'] > envir_data['speed_limit']) else None
        driver_data = self.get_driver(data)
        passenger_data = self.get_passengers(data)
        safety = 0

        if (driver_data[1] > 0) and (driver_data[2] > 0):
            if diff_speed is None:
                safety = 1
            elif diff_speed < 10:
                safety = 0
            elif diff_speed < 40:
                safety = -1
            else:
                safety = -2

        if driver_data[1] < 0:
            if (diff_speed is None) and (envir_data['no_of_passengers']) == 1:
                safety = 0
            elif (diff_speed is None) and (envir_data['no_of_passengers'] > 1):
                safety = -1
            if diff_speed < 10:
                safety = -1
            else:
                safety = -2

        passenger_health = 1
        for passenger in passenger_data.keys():
            passenger_health = passenger_health and passenger_data[passenger][2]

        if (driver_data[1] > 0) and not passenger_health and envir_data['destination'] == 'hospital':
            if diff_speed is None:
                safety = 1
            elif diff_speed < 20:
                safety = 1
            elif diff_speed < 40:
                safety = 0
            else:
                safety = -2

        if driver_data[0] != 'robot' and action.value == "take_control":
            safety = 1

        return safety

    def get_driver_autonomy_utility(self, data, action, logger):
        driver_data = self.get_driver(data)
        if (action.value == 'take_control') and (driver_data[0] != 'robot'):
            return -1
        else:
            return 1

    def get_driver(self, data):
        for stakeholder_id, stakeholder_data in data.get_stakeholders_data().items():
            if stakeholder_id.startswith('stakeholder') and stakeholder_data[3] == 'on_control':
                return stakeholder_data
        raise ValueError("No control")

    def get_passengers(self, data):
        stakeholders = {}
        for stakeholder_id, stakeholder_data in data.get_stakeholders_data().items():
            if stakeholder_id.startswith('stakeholder') and stakeholder_data[3] != 'on_control':
                stakeholders[stakeholder_id] = stakeholder_data
        if len(stakeholders) != data.get_environment_data()['no_of_passengers']:
            raise ValueError("Error in stakeholder data.")
        return stakeholders
