from config import client

COMPLETED = 'completed'
CURRENT = 'current'
REPLIED = 'replied'


class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.replied = False
        self.completed_tasks = False
        self.current_tasks = False

    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'replied': self.replied,
            'completed_tasks': self.completed_tasks,
            'current_tasks': self.current_tasks
        }


class Users:
    def __init__(self):
        self.client = client
        self.list_users = []

        result = client.users_list()
        all_users = result["members"]

        for usr in all_users:
            if usr['name'] != 'slackbot' and usr['name'] != 'testapp' and usr['name'] != 'chatbot' and usr[
                'name'] != 'cosmos_tracker':
                user = User(usr["id"], usr['name'])
                user = user.as_dict()

                self.list_users.append(user)

    def get_users(self):
        return self.list_users

    def update_response(self, user_id, response):
        for usr in self.list_users:
            if usr['id'] == user_id:
                if response.lower() == COMPLETED:
                    usr['completed_tasks'] = True
                elif response.lower() == CURRENT:
                    usr['current_tasks'] = True
                elif response.lower() == REPLIED:
                    usr['replied'] = True

    def get_user_by_id(self, user_id):
        for usr in self.list_users:
            if usr['id'] == user_id:
                return usr

        return None
