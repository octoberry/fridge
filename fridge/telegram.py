import requests


class Telegram(object):
    @staticmethod
    def push(message):
        requests.post("https://api.telegram.org/bot166098042:AAHrQYSoDCGkbTqIQvy_HvyMykou0Z5n1GU/sendMessage",
                      data={"text": message, "chat_id": "-41300273"})
