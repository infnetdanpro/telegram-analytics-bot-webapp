import celery

celery_app = celery.Celery("celery_app")
celery_app.config_from_object("celeryconfig")


@celery_app.task
def run_task(message):
    from config import config

    TOKEN = config["TELEGRAM_TOKEN"]
    bot = telebot.TeleBot(TOKEN)

    bot.reply_to(message, "Some data are ready!")
