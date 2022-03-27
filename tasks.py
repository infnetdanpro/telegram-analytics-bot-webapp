import celery
import celeryconfig


app = celery.Celery("celery_app")
app.config_from_object("celeryconfig")


@app.task
def run_task(reply_to: int):
    import telebot
    from config import config

    bot = telebot.TeleBot(config["TELEGRAM_TOKEN"])
    bot.send_message(reply_to, "Some data are ready!")
