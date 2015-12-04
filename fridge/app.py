from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.debug = True
# mongo = PyMongo(app)
# db = mongo.db['fridge']


class State(object):
    state = {}

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

state = State()
