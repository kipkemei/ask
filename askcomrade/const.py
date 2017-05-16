from collections import OrderedDict
from django.utils.timezone import utc
from datetime import datetime

LOCAL_MESSAGE, EMAIL_MESSAGE, NO_MESSAGES, DEFAULT_MESSAGES, ALL_MESSAGES = range(5)

MESSAGING_MAP = OrderedDict([
    (DEFAULT_MESSAGES, "default",),
    (LOCAL_MESSAGE, "local messagez",),
    (EMAIL_MESSAGE, "email",),
    (ALL_MESSAGES, "email for every new thread (mailing list mode)",),
])

MESSAGING_TYPE_CHOICES = MESSAGING_MAP.items()

USER_SORT_MAP = OrderedDict([
    ("recent visit", "-profile__last_login"),
    ("reputation", "-score"),
    ("date joined", "profile__date_joined"),
    # ("number of posts", "-score"),
    ("activity level", "-activity"),
])

USER_SORT_FIELDS = list(USER_SORT_MAP.keys())
# USER_SORT_DEFAULT = USER_SORT_FIELDS
USER_SORT_DEFAULT = USER_SORT_FIELDS[0]

USER_SORT_INVALID_MSG = "Invalid sort parameter received"

POST_SORT_MAP = OrderedDict([
    ("update", "-lastedit_date"),
    ("views", "-view_count"),
    ("followers", "-subs_count"),
    ("answers", "-reply_count"),
    ("bookmarks", "-book_count"),
    ("votes", "-vote_count"),
    ("rank", "-rank"),
    ("creation", "-creation_date"),
])

POST_SORT_FIELDS = list(POST_SORT_MAP.keys())
# POST_SORT_DEFAULT = POST_SORT_FIELDS
POST_SORT_DEFAULT = POST_SORT_FIELDS[0]

POST_SORT_INVALID_MSG = "Invalid sort parameter received"

POST_LIMIT_MAP = OrderedDict([
    ("all time", 0),
    ("today", 1),
    ("this week", 7),
    ("this month", 30),
    ("this year", 365),

])

POST_LIMIT_FIELDS = list(POST_LIMIT_MAP.keys())
# POST_LIMIT_DEFAULT = POST_LIMIT_FIELDS
POST_LIMIT_DEFAULT = POST_LIMIT_FIELDS[0]

POST_LIMIT_INVALID_MSG = "Invalid limit parameter received"


def now():
    return datetime.utcnow().replace(tzinfo=utc)
