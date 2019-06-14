from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
import requests
import os
import random


class IncisiveSkill(MycroftSkill):

    def __init__(self):
        super(IncisiveSkill, self).__init__(name="IncisiveSkill")
        
        # Initialize working variables used within the skill.
        self.sender_id = random.randint(1, 1000)
        self.checklist = False
        self.last_message = {'txt': ''}
        self.first_question = False

    def get_bot_response(self, message):
        url = os.environ.get('BACKEND_URL')
        rq = requests.post(url + '/bot/chat',
                           data={'sender': self.sender_id,
                                 'message': message})
        response = rq.json()
        return response

    @intent_handler(IntentBuilder("").require("Route"))
    def handle_route_feed_intent(self, message):
        response = self.get_bot_response(message.data.get('utterance'))

        for txt in response.get('text', []):
            self.speak(txt['text'])

    @intent_handler(IntentBuilder("").require("Checklist"))
    def handle_checklist_intent(self, message):
        response = self.get_bot_response(message.data.get('utterance'))
        self.checklist = True
        self.first_question = True
        for txt in response.get('text', []):
            self.last_message = txt
            self.speak(txt['text'], expect_response=True)

    @intent_handler(IntentBuilder("").require("Wait").require("Number"))
    def handle_wait_intent(self, message):
        number = message.data.get('Number')
        self.speak('I am going to remind you in {} minutes'.format(number))
        self.schedule_event(self.remind_question, int(number)*60, None, name='wait_utter')

    def remind_question(self):
        self.speak(self.last_message['txt'], expect_response=True)
        self.cancel_scheduled_event('mreminder')
        self.cancel_scheduled_event('no_resp_reminder')
        self.cancel_scheduled_event('wait_utter')

    def converse(self, utterances, lang='en-us'):
        if self.checklist:
            if not utterances and self.first_question:
                self.schedule_event(self.remind_question, 30,
                                    None, name='no_resp_reminder')
                return True
            elif self.voc_match(utterances[0], "No") and self.first_question:
                self.speak('I am going to remind you in 1 minute')
                self.schedule_event(self.remind_question, 60, None, name='mreminder')
                return True

            elif self.voc_match(utterances[0], "Yes") or self.voc_match(utterances[0], "No"):
                self.first_question = False
                response = self.get_bot_response(utterances[0])
                for txt in response.get('text', []):
                    self.checklist = 'done' not in txt['text']
                    self.speak(txt['text'], expect_response='done' not in txt['text'])
                return True
            return False
        return False


def create_skill():
    return IncisiveSkill()
