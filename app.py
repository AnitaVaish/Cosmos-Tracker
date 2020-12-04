from config import application
from schedule_message import schedule_message
import tracker_application

if __name__ == "__main__":
    schedule_message()
    application.run(port=6000, debug=False)
