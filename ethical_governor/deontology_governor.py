import ethical_governor.blackboard.blackboard as bb


class DeontologyGovernor:

    def __init__(self):
        self.blackboard = bb.Blackboard(conf='ethical_governor/elder_care_sim_deontology.yaml')

    def recommend(self, env):
        self.blackboard.load_data(env)
        self.blackboard.run_tests()
        recommendations = self.blackboard.recommend()
        print(recommendations)
        return recommendations
