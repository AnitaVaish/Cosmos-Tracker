import requests

from config import client

from utils.time import SATURDAY, SUNDAY
from utils.users import COMPLETED, CURRENT

SNOOZE = 'snooze'
SKIP = 'false'


class DefaultMessage:
    def __init__(self, user, scheduled_time=None):
        self.user = user
        self.scheduled_time = scheduled_time
        self.SCHEDULED_MESSAGE = []

    @staticmethod
    def _create_message(scheduled_time, user):
        user_id = user['id']
        username = user['username'].capitalize()

        message = {
            "user": user_id,
            "channel": f"@{user_id}",
            "post_at": scheduled_time,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hey *{username}*! :wave:\n"
                                f"Are you ready to fill out the *CT Daily Report*?"
                    },
                },
                {
                    "type": "actions",
                    "block_id": "actionblock789",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Yes, I'm ready!"
                            },
                            "style": "primary",
                            "value": "True"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Skip today's report!"
                            },
                            "style": "danger",
                            "value": "False"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Snooze"
                            },
                            "value": "Snooze"
                        },
                    ]
                }
            ]
        }

        if scheduled_time is not None:
            message["post_at"] = scheduled_time

        return message

    def send_message(self):
        message = self._create_message(None, self.user)

        response = client.chat_postMessage(channel=message['channel'],
                                           blocks=message['blocks'],
                                           text=message['blocks'][0]['text'])

        return response

    def schedule_message(self):
        message = self._create_message(self.scheduled_time, self.user)

        response = client.chat_scheduleMessage(channel=message['channel'],
                                               blocks=message['blocks'],
                                               text=message['blocks'][0]['text'],
                                               post_at=message['post_at'])

        message['response'] = response


class ResponseMessage:
    def __init__(self, user, text, response_url):
        self.user = user
        self.text = text
        self.response_url = response_url

    @staticmethod
    def _create_message(user, text):
        user_id = user['id']
        username = user['username'].capitalize()

        return {
            "user": user_id,
            "channel": f"@{user_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hey *{username}*! :wave:\n"
                                f"Are you ready to fill out the *CT Daily Report*? \n"
                                f">{text}\n"
                    },
                },
            ]
        }

    def update_message(self):
        message = self._create_message(self.user, self.text)

        response = requests.post(url=self.response_url, json=message)

        return response


class WeekendMessage:
    def __init__(self, user):
        self.user = user
        self.text = "It is `weekend`, no tasks for today! :tada:"

    def send(self):
        from utils.time import date, calendar

        today_day = date.today()

        day = calendar.day_name[today_day.weekday()]

        if day == SATURDAY or day == SUNDAY:
            user_id = self.user['id']

            client.chat_postMessage(channel=f"@{user_id}", text=self.text)


class Message:
    def __init__(self, user):
        self.user = user

    def send(self, response):
        text = ''
        user_id = self.user['id']
        username = self.user['username'].capitalize()

        if response.lower() == COMPLETED:
            text = f"Sure thing *{username}*, let's begin with the CT Daily Report. :sunglasses:\n\n" \
                   "What tasks did you complete yesterday?"

        elif response.lower() == SKIP:
            text = f"Ok *{username}* :sneezing_face:, " \
                   f"you can fill out the CT Daily report later by typing `daily`!"

        elif response.lower() == SNOOZE:
            text = f"Sure thing *{username}*, I will remind you in `15 minutes`! :wink:"

        client.chat_postMessage(channel=f'@{user_id}', text=text)
