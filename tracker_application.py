from flask import request, json

from config import application
from celery_conf import process_task

from utils.messages import DefaultMessage, ResponseMessage, Message
from utils.time import SetTimer
from utils.users import Users, User, COMPLETED, CURRENT, REPLIED

from config import client, slack_event_adapter, get_botID

from config import printer

BOT_ID = get_botID()

users = Users()

DAILY = 'daily'
SNOOZE = 'snooze'
SKIP = 'false'
TRUE = 'true'


@slack_event_adapter.on('message')
def event_message(payload):
    event = payload['event']

    user_id = event.get('user', None)

    user = users.get_user_by_id(user_id)

    if user is not None and user['id'] != BOT_ID:
        print(user)

        text = event['text']

        if text.lower() == DAILY and not user['replied']:
            default_message = DefaultMessage(user)
            default_message.send_message()

        if text.lower() != DAILY and not user['replied']:
            if user['completed_tasks'] and not user['current_tasks']:
                print("COMPLETED_TASKS")
                # printer.pprint(event)
                result = process_task.delay(user, event)

                # users.update_response(user_id, REPLIED)

                print(result)
                print(f'TASK_ID -> {result}')

                text = 'What are you planning to work on today?'

                client.chat_postMessage(channel=f'@{user_id}', text=text)

                users.update_response(user_id, CURRENT)

            elif user['completed_tasks'] and user['current_tasks']:
                print("CURRENTS_TASKS")
                # printer.pprint(event)

    return '', 200


@application.route('/interactive', methods=['POST'])
def message():
    payload = request.form.get('payload')

    data = json.loads(payload)

    user = User(data['user']['id'], data['user']['username'])
    user = user.as_dict()

    action_button_value = data['actions'][0]['value'].lower()
    response_url = data['response_url']

    if BOT_ID != user['id']:
        if action_button_value == SNOOZE:
            snooze_message = Message(user)
            snooze_message.send(SNOOZE)

            snooze_time = SetTimer.update(data['message']['ts'])

            response_message = ResponseMessage(user, "Snooze", response_url)
            response_message.update_message()

            default_message = DefaultMessage(user, snooze_time)
            default_message.schedule_message()

        elif action_button_value == TRUE:
            true_message = Message(user)
            true_message.send(COMPLETED)

            response_message = ResponseMessage(user, "Yes, I'm ready", response_url)
            response_message.update_message()

            users.update_response(user['id'], COMPLETED)

        elif action_button_value == SKIP:
            skip_message = Message(user)
            skip_message.send(SKIP)

            response_message = ResponseMessage(user, "Skip today's report!", response_url)
            response_message.update_message()

    return '', 200

# @slack_event_adapter.on('reaction_added')
# def reaction(payload):
#     pass
#
#
# @app.route('/daily', methods=['POST'])
# def message_count():
#     pass
