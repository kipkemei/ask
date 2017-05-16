from __future__ import absolute_import
from django.conf import settings
from celery.utils.log import get_task_logger
import os
from askcomrade import const
from datetime import timedelta

logger = get_task_logger(__name__)

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'askcomrade.settings')


app = Celery('askcomrade')

# Read the configuration from the config file.
app.config_from_object(settings.CELERY_CONFIG)

# Discover tasks in applications.
app.autodiscover_tasks(
    lambda: ["askcomrade.mailer", "askcomrade.awards"]
)


@app.task
def post_created(user):
    "Executed on a post creation"
    logger.info("post created")

@app.task
def call_command(name, *args, **kwargs):
    "Calls a django command in a delayed fashion"
    logger.info("calling django command %s with %s and %s" % (name, args, kwargs))
    from django.core.management import call_command
    call_command(name, *args, **kwargs)

@app.task
def test(*args, **kwds):
    logger.info("*** executing task %s %s, %s" % (__name__, args, kwds))
