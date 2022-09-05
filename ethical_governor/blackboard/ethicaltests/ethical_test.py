from abc import ABC, abstractmethod


class EthicalTest(ABC):
    def __init__(self, test_data):
        self.number_of_outputs = test_data['number_of_outputs']
        self.output_names = test_data['output_names']
        self.output = {}

    @abstractmethod
    def run_test(self, data, logger):
        """ run test for each action using the data available. Then populate the self.output dictionary as follows.
            - action 1:
                - column 1: data 1
                - column 2: data 2
                ...
            - action 2:
                - column 1: data 1
                - column 2: data 2
                ...
            ....
        """
        raise NotImplementedError("Please implement this method")
        pass

    def get_results(self):
        return self.output
