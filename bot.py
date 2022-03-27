import telebot
from flask import request

from app import app, bot
from config import config
from tasks import run_task


TOKEN = config["TELEGRAM_TOKEN"]


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello, " + message.from_user.first_name)


@bot.message_handler(content_types=["document"])
def handle_docs(message):
    # todo: get the document
    # todo: parse the document
    # todo: initialize the stats class
    reply_to = message.from_user.id
    task = run_task.delay(reply_to)
    bot.reply_to(message, "asdasd, " + message.from_user.first_name)


@app.route("/" + TOKEN, methods=["POST"])
def get_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/echo", methods=["GET"])
def echo():
    return "", 204


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://telegram-analytics-bot.herokuapp.com/" + TOKEN)
    return (
        '<center><h1><a href="https://t.me/chat_stats_analytics_bot">https://t.me/chat_stats_analytics_bot</a></h1></center>',
        200,
    )
