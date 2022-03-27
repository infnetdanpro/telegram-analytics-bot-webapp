import celery

app = celery.Celery("celery_app")
app.config_from_object("celeryconfig")


@app.task
def run_task(bot, message):
    print('CELERY!!!!!!!!!!')
    bot.reply_to(message, "Some data are ready!")
