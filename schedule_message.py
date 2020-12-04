from utils.time import SetTimer, SATURDAY, SUNDAY
from utils.users import Users
from utils.messages import DefaultMessage, WeekendMessage

users = Users()


def schedule_message():
    list_users = users.get_users()

    for user in list_users:
        timer = SetTimer(day=0, hour=17, minutes=27)

        scheduled_day = timer.get_day()

        if scheduled_day == SATURDAY or scheduled_day == SUNDAY:
            weekend_message = WeekendMessage(user)
            weekend_message.send()
        else:
            scheduled_time = timer.set()

            default_message = DefaultMessage(user, scheduled_time)

            default_message.schedule_message()

    return '', 200
