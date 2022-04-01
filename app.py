import json

import telebot
from flask import Flask, request

from config import config
from tasks import run_task

bot = telebot.TeleBot(config["TELEGRAM_TOKEN"])
app = Flask(__name__)

TOKEN = config["TELEGRAM_TOKEN"]


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Upload chat history for parsing data")


@bot.message_handler(content_types=["document"])
def handle_docs(message):
    # file_name = message.document.file_name
    file_id_info = bot.get_file(message.document.file_id)
    downloaded_file: bytes = bot.download_file(file_id_info.file_path)

    # in memory
    file = json.loads(downloaded_file.decode("utf-8"))
    bot.reply_to(
        message,
        "Your data is analyzing. Bot will message you then the result will be ready.",
    )

    # Put data in Celery App
    run_task.delay(reply_to=message.from_user.id, data_dict=file)


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
    bot.set_webhook(url="https://tg-chat-analytics.herokuapp.com/" + TOKEN)
    return (
        '<center><h1><a href="https://t.me/chat_stats_analytics_bot">'
        "https://t.me/chat_stats_analytics_bot</a></h1></center>",
        200,
    )
