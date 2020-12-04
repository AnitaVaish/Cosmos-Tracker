import requests

from config import conf


class PlaftormConnector:

    def __init__(self, email, password, auth_token):
        self.email = email
        self.password = password
        self.auth_token = auth_token

    def get_token(self):
        return self.auth_token

    def refresh_token(self):
        login_url = 'http://localhost:4000/api/login/'
        login_data = {
            'email': self.email,
            'password': self.password,
        }

        response = requests.post(url=login_url, json=login_data)

        new_token = response.json()['user']['token']

        auth_token = f'Bearer {new_token}'

        conf.set("Platform", "auth_token", auth_token)

        conf.write(open("conf.cfg", "w"))
