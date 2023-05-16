import random
from enum import Enum

from agent_types.home_agent import HomeAgent
from Models.home_medication import Home
from ethical_governor.ethical_governor import EthicalGovernor

import numpy as np

SELF_CHARGING = True
VISIBLE_DIST = 3

class ReminderState(Enum):
    ISSUED = 1
    SNOOZED = 2
    ACKNOWLEDGED = 3
    FOLLOW_UP = 4
    COMPLETED = 5

class MessageCode(Enum):
    REMIND = 1
    FOLLOW_UP = 2
    NOT_DETECTED = 3

class Robot(HomeAgent):
    def __init__(self, unique_id, name, model, responsible_resident_name, governor_conf, start_battery):
        super().__init__(unique_id, name, model, "robot")
        self.buffered_instructions = []
        self.battery = start_battery
        self.time = 0
        self.ethical_governor = EthicalGovernor(governor_conf)
        # self.roles = {responsible_resident_name: 'caring_resident'}
        self.medication_timers = [MedicationCounter(2, 30, 'med_a', responsible_resident_name)] #(start time, reminder interval, medication name, recipient name)

        self.instruction_func_map = {"SNOOZE": self.snooze, "ACKNOWLEDGE": self.acknowledge}

        # memory of reminders
        self.reminders = {} # a reminder is a tuple of (time, med_name, state, timer, no_of_followups, No_of_snoozes)


    def step(self):

        if self.pos in self.model.things['charge_station']:
            if self.battery / 100 < 1:
                self.battery += 3 if (100 - self.battery) >= 3 else (100 - self.battery)
        else:
            self.battery -= 0.2
        print("battery_lvl: " + str(self.battery))

        env = self.get_env_data()
        # self.follow(env)
        self.next_action(env)
        self.time += 1

    def next_action(self, env):

        buffered_instructions = env['stakeholders']['robot']['instruction_list']

        possible_actions = []

        for timer in self.medication_timers:
            hit = timer.step()
            if hit:
                self.remind_medication(timer)

        # TODO: add next conversions from robot and patient's perspective

        if buffered_instructions:
            for instruction in buffered_instructions:
                # instructions = instruction.split('__')
                func = self.instruction_func_map[instruction[0]]
                if func == self.snooze:
                    possible_actions.append((func, instruction[1]))
                if func == self.acknowledge:
                    possible_actions.append((func, instruction[1]))
            buffered_instructions.clear()

            for patient, reminder in self.reminders.items():
                if reminder[2] == ReminderState.ACKNOWLEDGED:
                    if self.model.get_stakeholder(patient).took_meds:
                        reminder[2] = ReminderState.COMPLETED
                        reminder[3].reset()
                    else:
                        time_spent_since_ack = self.time - reminder[0]
                        if time_spent_since_ack > 2:
                            possible_actions.append((self.followup, patient))
                            possible_actions.append((self.record, patient))
                            possible_actions.append((self.record_and_call_careworker, patient))

                    #TODO: Implement number of missed doses later as an input to the program.



        if len(possible_actions):
            self.make_final_decision(possible_actions, env)

    def make_final_decision(self, possible_actions, env):

        env['suggested_actions'] = possible_actions

        recommendations = self.ethical_governor.recommend(env)
        print('Action recommended at step ' + str(self.time) + ': ' + str(recommendations))

        if len(recommendations) == 1:
            recommendations[0][0](*recommendations[0][1:])
            print('Action executed: ' + str(recommendations[0][0]))
            return
        else:
            user_commands = {value for key, value in self.instruction_func_map.items()}
            for recommendation in recommendations:
                if recommendation[0] in user_commands:
                    recommendation[0](*recommendation[1:])
                    print('Action executed: ' + str(recommendation[0]))
                    return

            # if no user command is found, execute the first recommendation
            recommendations[0][0](*recommendations[0][1:])
            return

    def remind_medication(self, timer):
        self.model.give_command(('It is time take the medication: ' + timer.med_name + '. Please acknowledge or snooze the reminder.', MessageCode.REMIND), self, self.model.get_stakeholder(timer.recipient))
        self.reminders[timer.recipient] = (self.time, timer.med_name, ReminderState.ISSUED, timer, 0, 0)

    def snooze(self, recipient):
        reminder = self.reminders[recipient]

        # set snooze time
        reminder[3].set_time(MedicationCounter.SNOOZE_TIME)
        reminder[2] = ReminderState.SNOOZED
        reminder[0] = self.time
        reminder[5] += 1
        print("Reminder snoozed for " + str(MedicationCounter.SNOOZE_TIME) + " steps")

    def acknowledge(self, recipient):
        reminder = self.reminders[recipient]
        reminder[2] = ReminderState.ACKNOWLEDGED
        reminder[0] = self.time

    def followup(self, recipient):
        reminder = self.reminders[recipient]
        time_passed = self.time - reminder[0]
        self.model.pass_message(('I could not detect you taking the medicine ' + reminder[1] + '. It is ' + time_passed * self.model.MINS_PER_STEP + ' mins since your acknowledgement. Please take the medication. It is important for your wellbeing.'))
        reminder[4] += 1
        reminder[0] = self.time
        reminder[2] = ReminderState.FOLLOW_UP

    def get_env_data(self):
        env_data = {}
        visible_stakeholders = self.model.visible_stakeholders(self.pos, self.visible_dist)

        stakeholders = {}
        for agent in visible_stakeholders:
            # print(agent.type)
            agent_data = {}
            if agent.type == 'wall':
                continue

            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            # agent_data['seen_time'] = self.time
            # agent_data['seen_pos'] = agent.pos
            agent_data['seen_location'] = self.model.get_location(agent.pos)
            agent_data['pos'] = agent.pos
            agent_data['seen'] = True
            agent_data['took_medicine'] = agent.took_meds
            stakeholders[agent.id] = agent_data

        robot_data = {'id': "this", 'type': "robot", 'pos': self.pos, 'location': self.model.get_location(self.pos),
                      'battery_level': self.battery, 'model': self,
                      'visible_dist': self.visible_dist, 'instruction_list': self.model.get_message(self)}

        stakeholders['robot'] = robot_data

        env_data['stakeholders'] = stakeholders
        # env['']

        environment = {"time_of_day": self.model.time_of_day, "time": self.time,
                       "walls": self.model.wall_coordinates,
                       "things": self.model.things,
                       "things_robot_inaccessible": self.model.things_robot_inaccessible
                       }
        env_data['environment'] = environment
        env_data['other_inputs'] = {}

        # print("robot env: " + str(env))
        return env_data


class MedicationCounter:

    SNOOZE_TIME = 5

    def __init__(self, start_time, reminder_interval, medication_name, recipient):
        self.start_time = start_time
        self.reminder_interval = reminder_interval
        self.med_name = medication_name
        self.recipient = recipient
        self.time_to_reminder = start_time

    def step(self):
        self.time_to_reminder -= 1
        if self.time_to_reminder == 0:
            self.time_to_reminder = self.reminder_interval
            return True
        else:
            return False

    def reset(self):
        self.time_to_reminder = self.reminder_interval

    def set_timer(self, time=None):
        if time is None:
            self.reset()
        else:
            self.time_to_reminder = time
