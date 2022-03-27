import telebot

from flask import Flask

from config import config


bot = telebot.TeleBot(config["TELEGRAM_TOKEN"])
app = Flask(__name__)

import bot


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
