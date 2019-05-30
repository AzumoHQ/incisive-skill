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
        for txt in response.get('text', []):
            self.speak(txt['text'], expect_response=True)

    def converse(self, utterances, lang='en-us'):
        if self.checklist:
            if self.voc_match(utterances[0], "Yes") or self.voc_match(utterances[0], "No"):
                response = self.get_bot_response(utterances[0])
                for txt in response.get('text', []):
                    self.checklist = 'done' not in txt['text']
                    self.speak(txt['text'], expect_response='done' not in txt['text'])
                return True
            return False
        return False


def create_skill():
    return IncisiveSkill()
