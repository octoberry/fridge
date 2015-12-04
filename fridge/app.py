from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.config.from_pyfile('default_settings.py')
mongo = PyMongo(app)


class State(object):
    state = {}

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

state = State()
