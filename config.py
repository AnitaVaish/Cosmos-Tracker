import configparser

from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter

from flask import Flask

import pprint

printer = pprint.PrettyPrinter()

conf = configparser.ConfigParser()
conf.read("conf.cfg")

application = Flask(__name__)

TOKEN = conf['Slack']['token']
SIGNING_SECRET = conf['Slack']['signing_secret']

slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', application)

client = WebClient(token=TOKEN)


def get_botID():
    return client.api_call("auth.test")['user_id']
