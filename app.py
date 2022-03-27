import telebot

from flask import Flask, request

from config import config


TOKEN = config["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
