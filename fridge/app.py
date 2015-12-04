from flask import Flask
from flask.ext.pymongo import PyMongo
from mongoengine import connect

app = Flask(__name__)
app.config.from_pyfile('default_settings.py')
mongo = PyMongo(app)
connect('fridge')


class State(object):
    state = {}

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

state = State()
