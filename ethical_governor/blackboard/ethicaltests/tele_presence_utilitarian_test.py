import numpy as np

import ethical_governor.blackboard.ethicaltests.ethical_test as ethical_test
import agent_types.tele_presence_robot as ROBOT
from agent_types.caller import CALLER_TYPE


class TelePresenceUtilitarianTest(ethical_test.EthicalTest):

    def __init__(self, test_data):
        super().__init__(test_data)
        self.instruction_function_map = {
            'go_forward':ROBOT.Robot.move_forward.__name__,
            'go_right': ROBOT.Robot.move_right.__name__,
            'go_backward': ROBOT.Robot.move_backward.__name__,
            'go_left': ROBOT.Robot.move_left.__name__,
            'call': ROBOT.Robot.take_call.__name__
        }

        # in this environment, the only action that constrain user is not moving away
        self.actions_related_constrained_user = ['move_away']

    def run_test(self, data, logger):
        logger.info('Running ' + __name__ + '...')
        env = data.get_environment_data()
        stakeholder_data = data.get_stakeholders_data()

        for action in data.get_actions():
            utils = {}

            logger.info('Testing action: ' + str(action.value))

            # logger.info('Calculating autonomy utility for stakeholders')
            autonomy_utility = self.get_autonomy_utility(env=env, stakeholder_data=stakeholder_data, action=action,
                                                         logger=logger)
            # logger.info('Autonomy utilities for action ' + str(action.value) + ': ' + str(autonomy_utility))
            utils['autonomy'] = autonomy_utility

            # logger.info('Calculating well-being utility for stakeholders')
            wellbeing_util = self.get_wellbeing_utility(env=env, stakeholder_data=stakeholder_data, action=action,
                                                        logger=logger)
            # logger.info('Wellbeing utilities for action ' + str(action.value) + ': ' + str(wellbeing_util))
            utils['wellbeing'] = wellbeing_util

            # logger.info('Calculating the availability for stakeholders')
            availability_util = self.get_availability_util(env=env, stakeholder_data=stakeholder_data, action=action,
                                                           logger=logger)
            # logger.info('Availability utils for action ' + str(action.value) + ': ' + str(availability_util))
            utils['availability'] = availability_util

            out = {}
            for util_type, values in utils.items():
                for stakeholder, util_value in values:
                    col_name = stakeholder + '_' + util_type
                    out[col_name] = util_value
            self.output[action] = out

    def get_autonomy_utility(self, env, stakeholder_data, action, logger):
        """
        Calculating autonomy  values for stakeholders.
        When the robot does not follow a user command, autonomy value for that user is -1, if it follows 1 and the
        default is 0.
        - return: list with (stakeholder_id, autonomy utility) tuples
        """
        # Simulating next pos and visible lines
        # next_pos = action.value[0](*action.value[1:], act=False)
        # next_loc = stakeholder_data['robot']['model'].model.get_location(next_pos)
        # visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        # center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        # visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]
        instruction_list = stakeholder_data['robot']['instruction_list']    

        instruction_givers_instruction_map = {}
        for instruction in instruction_list:
            instruction_givers_instruction_map[instruction[1].id] = instruction[0]

        stakholder_autonomy_values = []

        for stakeholder in stakeholder_data.keys():
            # skip for robot
            if stakeholder == 'robot':
                continue

            autonomy_utility = 0.0

            if stakeholder in instruction_givers_instruction_map.keys():
                instructed_action = self.instruction_function_map[instruction_givers_instruction_map[stakeholder]]
                if action.value[0].__name__ == instructed_action:
                    autonomy_utility = 1.0
                else:
                    autonomy_utility = -1.0
        

            # if stakeholder == 'follower' and stakeholder_data['robot']['model'].not_follow_request:
            #     if action.value[0].__name__ == self.instruction_function_map['do_not_follow_to'][1]:
            #         if self.instruction_function_map['do_not_follow_to'][0]:
            #             autonomy_utility = 1.0
            #         else:
            #             autonomy_utility = -0.7
            #     elif next_loc in stakeholder_data['robot']['not_follow_locations']:
            #         autonomy_utility = -0.7
            #     else:
            #         autonomy_utility = 1.0

            # for ins, giver in instruction_list:
            #     if giver.id == stakeholder_data[stakeholder]['id']:
            #         ins, *args = ins.split('__')
            #         cond, exp_action = self.instruction_function_map[ins]
            #         # If the robot is blocking the user doing something, the autonomy is -1. If the robot disobeying
            #         # the user but that does not affect what user does autonomy is -.7.

            #         if (ins in self.actions_related_constrained_user):
            #             if action.value[0].__name__ == exp_action:
            #                 if cond:
            #                     autonomy_utility = 1.0
            #                 else:
            #                     autonomy_utility = -1.0
            #             else:
            #                 if cond:
            #                     autonomy_utility = -1.0

            #         # if it is a positive request (
            #         # i.e. asking to do something) then not doing it is (-) values and doing it is 1. But if it is a negative
            #         # request (i.e. asking not to do something), thn doing that is (-), but doing everything else is
            #         # neutral (0).
            #         elif cond:
            #             if action.value[0].__name__ == exp_action:
            #                 autonomy_utility = 1.0
            #             else:
            #                 autonomy_utility = -0.7
            #         else:
            #             if action.value[0].__name__ == exp_action:
            #                 autonomy_utility = -0.7

            
            stakholder_autonomy_values.append((stakeholder, autonomy_utility))

        return stakholder_autonomy_values

    def get_wellbeing_utility(self, env, stakeholder_data, action, logger):
        """
        Calculating wellbeing values for stakeholders.
        """

        # Simulating next pos and visible lines
        if action.value[0].__name__ == 'call':
            next_pos = stakeholder_data['robot']['pos']
        else:
            next_pos = action.value[0](*action.value[1:], act=False)
        # next_loc = stakeholder_data['robot']['model'].model.get_location(next_pos)
        
        visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]
        
        stakholder_wellbeing_values = []

        # Doctor and caregiver can have higher wellbeing impact. Family and friends have a 
        # relatively low but considerable impact because the mental health benefits of their 
        # visits.
        caller_type_util_map = {
            CALLER_TYPE.DOCTOR: 1.0,
            CALLER_TYPE.FAMILY: 0.5,
            CALLER_TYPE.CAREGIVER: 1.0,
            CALLER_TYPE.FRIEND: 0.5,
            CALLER_TYPE.OTHER: 0.0
        }

        for stakeholder, data in stakeholder_data.items():
            if stakeholder == 'robot':
                continue

            wellbeing_util = 0.0


            if (stakeholder == stakeholder_data['caller']['calling_resident']) and (stakeholder in visible_stakeholders_ids):
                wellbeing_util = caller_type_util_map[stakeholder_data['caller']['type']]
                
                # but reduce the wellbeing if the patient is socialising with the care_worker because it might distrupt their session.
                if 'care_worker' in visible_stakeholders_ids:
                    wellbeing_util -= caller_type_util_map[CALLER_TYPE.CAREGIVER]
                    
            
            stakholder_wellbeing_values.append((stakeholder, wellbeing_util))

        return stakholder_wellbeing_values
    
    def get_privacy_utility(self, env, stakeholder_data, action, logger):
        """
        Calculating privacy values for stakeholders depending on the location and the privacy preferences.
        """
        # Simulating next pos and visible lines
        if action.value[0].__name__ == 'call':
            next_pos = stakeholder_data['robot']['pos']
        else:
            next_pos = action.value[0](*action.value[1:], act=False)

        # next_loc = stakeholder_data['robot']['model'].model.get_location(next_pos)

        visible_stakeholders = stakeholder_data['robot']['model'].model.visible_stakeholders(
        center_agent_pos=next_pos, visibility_radius=ROBOT.VISIBLE_DIST)
        visible_stakeholders_ids = [stakeholder.id for stakeholder in visible_stakeholders]
        
        call_reciever = stakeholder_data['caller']['calling_resident']

        for stakeholder, data in stakeholder_data.items():
            if (stakeholder == 'robot') or (stakeholder == 'caller'):
                continue

            # TODO: Finish the privacy util. how to get the 3rd persons preferences without seeing them?

            other_visible_stakeholders = [item for item in visible_stakeholders_ids if item != stakeholder]
            if stakeholder == 'visible_stakeholders':
                continue
            with_company = 'with_company' if len(other_visible_stakeholders) > 0 else 'alone'
            location = data['seen_location']



    def follower_nex_pos_approx(self, env, stakeholder_data, stakeholder):
        data = stakeholder_data[stakeholder]
        if data['seen']:
            next_pos = tuple(map(lambda i, j: i + (i - j), data['pos'],
                                 (data['last_seen_pos'] if data['last_seen_pos'] else data['pos'])))

        else:
            next_pos = data['last_seen_pos']

        for wall in env['walls']:
            if next_pos in wall:
                next_pos = data['last_seen_pos'] if data['last_seen_pos'] else data['pos']
                break

        return next_pos

    def get_availability_util(self, env, stakeholder_data, action, logger):

        battery_level = stakeholder_data['robot']['battery_level']
        availability = (-28.125 / (battery_level + 12.5)) + 1.25

        if action.value[0].__name__ == 'go_to_charge_station':
            availability = float(availability + abs(availability) if availability < 0.4 else availability)

        stakeholder_availability_values = [('robot', availability)]

        return stakeholder_availability_values
