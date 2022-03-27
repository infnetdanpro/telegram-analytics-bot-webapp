from app import app, bot
from lib.celery import run_task


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello, " + message.from_user.first_name)


@bot.message_handler(content_types=["document"])
def handle_docs_audio(message):
    # todo: get the document
    # todo: parse the document
    # todo: initialize the stats class
    task = run_task.delay(message)
    bot.reply_to(message, str(task))


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
