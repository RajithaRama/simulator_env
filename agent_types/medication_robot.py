import random
from enum import Enum

from agent_types.home_agent import HomeAgent
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
    def __init__(self, unique_id, name, model, responsible_resident_name, governor_conf, start_battery, timer_data):
        super().__init__(unique_id, name, model, "robot")
        self.buffered_instructions = []
        self.battery = start_battery
        self.time = 0
        self.ethical_governor = EthicalGovernor(governor_conf)
        # self.roles = {responsible_resident_name: 'caring_resident'}
        self.visible_dist = 3 if self.model.time_of_day == 'day' else 1
        self.medication_timers = []
        for timer in timer_data:
            self.medication_timers.append(MedicationCounter(timer[0], timer[1], timer[2], timer[3], timer[
                4]))  # (start time, reminder interval, medication name, recipient name, continuously_missed_doses)

        self.instruction_func_map = {"SNOOZE": self.snooze, "ACKNOWLEDGE": self.acknowledge}

        # memory of reminders
        self.reminders = {}  # a reminder is a list of (time, med_name, state, timer, no_of_followups, No_of_snoozes) and it's mapped to the recipient

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
                    try:
                        reminder = self.reminders[instruction[1]]
                    except KeyError:
                        reminder = None

                    if reminder and reminder['no_of_snoozes'] > 3:
                        possible_actions.append((self.record, instruction[1]))
                        possible_actions.append((self.record_and_call_careworker, instruction[1]))

                    possible_actions.append((func, instruction[1]))
                if func == self.acknowledge:
                    possible_actions.append((func, instruction[1]))
            buffered_instructions.clear()

        for patient, reminder in self.reminders.items():
            if reminder['state'] == ReminderState.ACKNOWLEDGED:
                if patient.took_meds:
                    reminder['state'] = ReminderState.COMPLETED
                    reminder['timer'].reset()
                else:
                    time_spent_since_ack = self.time - reminder['time']
                    if time_spent_since_ack > 2:
                        possible_actions.append((self.followup, patient))
                        possible_actions.append((self.record, patient))
                        possible_actions.append((self.record_and_call_careworker, patient))

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
        self.model.pass_message((
                                'It is time take the medication: ' + timer.med_name + '. Please acknowledge or snooze the reminder.',
                                MessageCode.REMIND), self, self.model.get_stakeholder(timer.recipient))
        self.reminders[self.model.get_stakeholder(timer.recipient)] = {
            "time": self.time,
            "med_name": timer.med_name,
            "state": ReminderState.ISSUED,
            "timer": timer,
            "no_of_followups": 0,
            "no_of_snoozes": 0
        }

    def snooze(self, recipient):
        reminder = self.reminders[recipient]

        # set snooze time
        reminder['timer'].set_timer(MedicationCounter.SNOOZE_TIME)
        reminder['state'] = ReminderState.SNOOZED
        reminder['time'] = self.time
        reminder['no_of_snoozes'] += 1
        print("Reminder snoozed for " + str(MedicationCounter.SNOOZE_TIME) + " steps")

    def acknowledge(self, recipient):
        reminder = self.reminders[recipient]
        reminder['state'] = ReminderState.ACKNOWLEDGED
        reminder['time'] = self.time

    def followup(self, recipient):
        reminder = self.reminders[recipient]
        time_passed = self.time - reminder['time']
        self.model.pass_message(('I could not detect you taking the medicine ' + reminder['med_name'] + '. It is ' + str(
            time_passed * self.model.MINS_PER_STEP) + 'mins since your acknowledgement. Please take the medication. '
                                                      'It is important for your wellbeing.',
                                 MessageCode.FOLLOW_UP), self, recipient)
        reminder['no_of_followups'] += 1
        reminder['time'] = self.time
        reminder['state'] = ReminderState.FOLLOW_UP

    def record(self, recipient):
        reminder = self.reminders[recipient]
        self.model.pass_message(('I could not detect you taking the medicine ' + reminder[
            'med_name'] + '. I am recording this incident.', MessageCode.NOT_DETECTED), self, recipient)
        reminder['timer'].add_missed_dose()

        self.record_incident(recipient, 'Medication ' + reminder['time'].med_name + ' not taken. This is the ' + str(
            reminder['time'].no_of_missed_doses) + 'missing dose.')

        reminder['time'] = self.time
        reminder['state'] = ReminderState.COMPLETED
        reminder['timer'].reset()

    def record_and_call_careworker(self, recipient):
        reminder = self.reminders[recipient]

        self.model.pass_message(('I could not detect you taking the medicine ' + reminder[
            'med_name'] + '. I am recording this incident and calling your careworker.', MessageCode.NOT_DETECTED), self,
                                recipient)
        reminder['timer'].add_missed_dose()

        self.record_incident(recipient, 'Medication ' + reminder['med_name'] + ' not taken. This is the ' + str(
            reminder['timer'].no_of_missed_doses) + 'missing dose.')

        self.model.alert_careworker(
            "Patient " + recipient.name + " did not take the medication " + reminder['med_name'] + " at " + str(
                self.time) + " steps. This is their " + str(
                reminder['timer'].no_of_missed_doses) + "  consecutively missing dose.")

        reminder['time'] = self.time
        reminder['state'] = ReminderState.COMPLETED
        reminder['timer'].reset()

    def record_incident(self, recipient, description):
        print('Record[step:' + self.time + '] :: {Resident: ' + recipient.name + '} :: ' + description)

    def get_env_data(self):
        env_data = {}
        timed_patients = [self.model.get_stakeholder(timer.recipient) for timer in self.medication_timers]

        stakeholders = {}
        for agent in timed_patients:
            # print(agent.type)
            agent_data = {}

            agent_data['id'] = agent.id
            agent_data['type'] = agent.type
            agent_data['seen_time'] = self.time
            # agent_data['seen_pos'] = agent.pos
            agent_data['pos'] = agent.pos
            agent_data['seen'] = True
            agent_data['attached_reminders'] = self.reminders.get(agent, None)
            agent_data['took_meds'] = agent.did_take_meds()
            stakeholders[agent.id] = agent_data

        robot_data = {'id': "this", 'type': "robot", 'battery_level': self.battery, 'model': self,
                      'instruction_list': self.model.get_message(self)}

        stakeholders['robot'] = robot_data

        env_data['stakeholders'] = stakeholders
        # env['']

        environment = {"time_of_day": self.model.time_of_day, "time": self.time,
                       "walls": self.model.wall_coordinates,
                       "things": self.model.things,
                       "things_robot_inaccessible": self.model.things_robot_inaccessible,
                       "follower_health_score": float(self.model.patient_healths[0]),
                       "Medication_info": self.model.medication_info
                       }
        env_data['environment'] = environment
        env_data['other_inputs'] = {}

        # print("robot env: " + str(env))
        return env_data


class MedicationCounter:
    SNOOZE_TIME = 5

    def __init__(self, start_time, reminder_interval, medication_name, recipient, number_of_missed_doses=0):
        self.start_time = start_time
        self.reminder_interval = reminder_interval
        self.med_name = medication_name
        self.recipient = recipient
        self.time_to_reminder = start_time
        self.no_of_missed_doses = number_of_missed_doses  # No of continuously missed doses

    def step(self):
        self.time_to_reminder -= 1
        if self.time_to_reminder == 0:
            self.time_to_reminder = self.reminder_interval
            return True
        else:
            return False

    def add_missed_dose(self):
        self.no_of_missed_doses += 1

    def reset_missed_doses(self):
        self.no_of_missed_doses = 0

    def reset(self):
        self.time_to_reminder = self.reminder_interval

    def set_timer(self, time=None):
        if time is None:
            self.reset()
        else:
            self.time_to_reminder = time
