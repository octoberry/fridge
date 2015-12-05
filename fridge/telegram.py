import requests


class Telegram(object):
    @staticmethod
    def push(message, chat_id):
        requests.post("https://api.telegram.org/bot166098042:AAHrQYSoDCGkbTqIQvy_HvyMykou0Z5n1GU/sendMessage",
                      data={"text": message, "chat_id": chat_id})
