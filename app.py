import os

from dotenv import dotenv_values
from flask import Flask, request

import telebot

config = {**dotenv_values(".env"), **os.environ}


TOKEN = config["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello, " + message.from_user.first_name)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_message(message):
    bot.reply_to(message, message.text)


@app.route("/" + TOKEN, methods=["POST"])
def get_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/", methods=["GET"])
def index():
    return (
        '<center><h1><a href="http://t.me/chat_stats_analytics_bot">http://t.me/chat_stats_analytics_bot</a></h1></center>',
        200,
    )


@app.route("/echo", methods=["GET"])
def echo():
    return "", 204


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://telegram-analytics-bot.herokuapp.com/" + TOKEN)
    return "!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
