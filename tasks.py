import celery
import celeryconfig
import telebot

from config import config
from lib.stat import JSONLogParser


app = celery.Celery("celery_app")
app.config_from_object("celeryconfig")

bot = telebot.TeleBot(config["TELEGRAM_TOKEN"]) 


@app.task
def run_task(self, reply_to: int, file_id: str):
    data = JSONLogParser(file_name=file_name)
    data.get_most_replied_user()
    bot.send_message(reply_to, data.users_replies_stats)
