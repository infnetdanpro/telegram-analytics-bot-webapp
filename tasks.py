import os
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, ChoiceLoader, select_autoescape

import celery
import celeryconfig
import telebot

from config import config
from lib.stat import JSONLogParser


app = celery.Celery("celery_app")
app.config_from_object("celeryconfig")

bot = telebot.TeleBot(config["TELEGRAM_TOKEN"])

path = os.path.join(os.getcwd(), "templates")
loader = ChoiceLoader([FileSystemLoader(path)])
env = Environment(
    loader=loader,
    autoescape=select_autoescape(),
)

def prepare_template_data(report):
    hashtags_frequency = {
        k: v
        for k, v in sorted(
            report["hashtags_frequency"].items(), key=lambda item: -item[1]
        )
    }
    hashtags_frequency = {
        "chart_labels": [f"'{e}'" for e in hashtags_frequency.keys()],
        "chart_values": [e for e in hashtags_frequency.values()],
    }

    word_stats = {
        k: v
        for k, v in sorted(report["word_stats"].items(), key=lambda item: -item[1])
        if v > 1
    }
    word_stats = {
        "chart_labels": [f"'{e}'" for e in word_stats.keys()][:250],
        "chart_values": [e for e in word_stats.values()][:250],
    }

    most_replies = {
        k: v
        for k, v in sorted(report["most_replies"].items(), key=lambda item: -item[1])
        if v >= 1
    }
    most_replies = {
        "chart_labels": [f"'{e}'" for e in most_replies.keys()][:250],
        "chart_values": [e for e in most_replies.values()][:250],
    }

    unique_hashtags = report["unique_hashtags"]

    data = {
        "hashtags_frequency": {
            "data": hashtags_frequency,
            "type": "pie",
            "title": "Hashtag frequency (all)",
        },
        "unique_hashtags": {
            "data": unique_hashtags,
            "type": "cloud",
            "title": "List of unique of hashtags (all)",
        },
        "word_stats": {
            "data": word_stats,
            "type": "pie",
            "title": "Word stats (top 250)",
        },
        "most_replies": {
            "data": most_replies,
            "type": "bar",
            "title": "Most replied users (top 250)",
        },
    }
    
    return data


@app.task
def run_task(reply_to: int, data_dict: dict):
    data = JSONLogParser(data_dict=data_dict)
    report = data.generate_stats()
    template = env.get_template("report.html")
    
    # prepare data and render template
    chart_data = prepare_template_data(report=report)
    template_data = template.render(chart_data=chart_data, chat_name=data.name)

    obj = BytesIO(template_data)
    obj.name = f'{data.id}.html'
    bot.send_document(chat_id=reply_to, data=obj, caption='your file')

    # bot.send_document(chat_id=reply_to, data=template_data, visible_file_name=path)
