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
    file_name = message.document.file_name
    file_id_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_id_info.file_path)

    # in memory
    file = json.loads(downloaded_file.decode("utf-8"))

    task = run_task.delay(reply_to=message.from_user.id, data_dict=file)
    bot.reply_to(
        message,
        "Your data is analyzing. Bot will message you then the result will be ready.",
    )


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


if __name__ == "__main__":
    bot.infinity_polling()
