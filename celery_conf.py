from celery import Celery

from config import application, conf
from utils.platform import PlaftormConnector
from utils.time import date

from config import printer

import requests

RABBITMQ_USER = conf['RabbitMQ']['user']
RABBITMQ_PASSWORD = conf['RabbitMQ']['rabbit_password']
RABBITMQ_IP = conf['RabbitMQ']['ip']


def make_celery(app):
    celery = Celery(
        application.import_name,
        broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_IP}',
    )

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_worker = make_celery(application)


class Entry:

    def __init__(self, user, task):
        self.user = user
        self.task = task

        self.CHATBOT_EMAIL = conf['Platform']['email']
        self.CHATBOT_PASSWORD = conf['Platform']['platform_password']
        self.CHATBOT_AUTH_TOKEN = conf['Platform']['auth_token']

    def create(self):
        text = self.task['text']

        today_date = date.today()

        url = 'http://localhost:4000/api/records/chatbot/'

        data = {
            'data': {
                'date': str(today_date),
                'user': self.user['username'].capitalize(),
                'task': text,
            }
        }

        platform_connector = PlaftormConnector(self.CHATBOT_EMAIL, self.CHATBOT_PASSWORD, self.CHATBOT_AUTH_TOKEN)

        auth_token = platform_connector.get_token()

        response = requests.post(url=url, json=data, headers={'Authorization': auth_token}).json()

        if not response['success']:
            platform_connector.refresh_token()

            refreshed_auth_token = platform_connector.get_token()

            response = requests.post(url=url, json=data, headers={'Authorization': refreshed_auth_token}).json()

            response['success'] = True

    def delete(self):
        pass

    def update(self):
        pass


@celery_worker.task(name='process_task')
def process_task(user, task):
    entry = Entry(user, task)
    entry.create()

    return '', 200
