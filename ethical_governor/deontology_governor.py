import ethical_governor.blackboard.blackboard as bb


class DeontologyGovernor:

    def __init__(self):
        self.blackboard = bb.Blackboard(conf='elder_care_sim_deontology.yaml')

    def recommend(self):
        self.blackboard.load_data()
        self.blackboard.run_tests()
        recommendations = self.blackboard.recommend()
        print(recommendations)
        return recommendations
