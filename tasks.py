import celery
import celeryconfig
import telebot

from config import config
from lib.stat import JSONLogParser


app = celery.Celery("celery_app")
app.config_from_object("celeryconfig")

bot = telebot.TeleBot(config["TELEGRAM_TOKEN"]) 


@app.task(bind=True)
def run_task(self, reply_to: int, data_dict: dict):
    task_id = self.request.id
    data = JSONLogParser(data_dict=data_dict)
    data.get_most_replied_user()
    # todo: generate data for html
    bot.send_message(reply_to, task_id)
