import celery

app = celery.Celery("celery_app")
app.config_from_object("celeryconfig")


@app.task
def run_task(message):
    from config import config

    TOKEN = config["TELEGRAM_TOKEN"]
    bot = telebot.TeleBot(TOKEN)

    bot.reply_to(message, "Some data are ready!")
