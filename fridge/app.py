from flask import Flask
from flask.ext.pymongo import PyMongo
from mongoengine import connect

app = Flask(__name__)
app.config.from_pyfile('default_settings.py')
mongo = PyMongo(app)
connect('fridge')


class Cart(object):
    status = 'new'

cart = Cart()
