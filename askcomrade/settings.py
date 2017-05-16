import os
import djcelery
djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'hsuw-xuy!ny!81ag(g&4q&h$fjj43paqk$(cx#69b5y_ex*wgk'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','askcomrade.herokuapp.com', '0.0.0.0', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'django.contrib.humanize',
    'django.contrib.flatpages',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.instagram',
    'allauth.socialaccount.providers.twitter',

    'haystack',
    'crispy_forms',

    # 'compressor',
    # """ Askcomrade specific apps"""
    'askcomrade.apps.users',
    'askcomrade.apps.util',
    'askcomrade.apps.posts',
    'askcomrade.apps.badges',
    'askcomrade.apps.planet',
    'askcomrade.apps.messagez',
    # 'askcomrade',

    'askcomrade.server',
    'djcelery',
    'kombu.transport.django',
    'captcha',
    'django.contrib.sites',
]


MIDDLEWARE = [
    'askcomrade.server.middleware.SSLMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'askcomrade.server.middleware.Visit',
]


ROOT_URLCONF = 'askcomrade.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'askcomrade/server/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'django.template.loaders.filesystem.Loader',
                # 'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]


WSGI_APPLICATION = 'askcomrade.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# import dj_database_url
# db_from_env = dj_database_url.config()
# DATABASES['default'].update(db_from_env)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

ALLOWED_TAGS = "p div br code pre h1 h2".split()
ALLOWED_TAGS += "h3 h4 hr span s sub sup b i img strong strike em underline super table thead tr th td tbody".split()
ALLOWED_STYLES = 'color font-weight background-color width height'.split()
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing'],

}

DEFAULT_MESSAGE_PREF = "local"

AUTH_USER_MODEL = 'users.User'

__DEFAULT_HOME = os.path.join(BASE_DIR, "..")
__DEFAULT_DATABASE_NAME = 'default.db'
__DEFAULT_ASKCOMRADE_ADMIN_NAME = "Askcomrade Admin"
__DEFAULT_ASKCOMRADE_ADMIN_EMAIL = "admin@asks.me"
__DEFAULT_SECRET_KEY = 'admin@askc.me'
__DEFAULT_SITE_DOMAIN = 'www.kipkemei.com'
__DEFAULT_FROM_EMAIL = 'noreply@askcomrade.com'

SITE_ID = 1
SITE_NAME = ""
SITE_DOMAIN = __DEFAULT_SITE_DOMAIN


RECENT_VOTE_COUNT = 7
RECENT_USER_COUNT = 7
RECENT_POST_COUNT = 12

POST_VIEW_MINUTES = 5

CACHE_TIMEOUT = 60

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache' if DEBUG
        else 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}


INTERNAL_IPS = ('127.0.0.1',)

HOME_DIR = os.path.join(BASE_DIR, 'home')

LIVE_DIR = os.path.join(BASE_DIR, 'live')

EXPORT_DIR = os.path.join(LIVE_DIR, "export")
STATIC_ROOT = os.path.join(EXPORT_DIR, "static")

PLANET_DIR = os.path.join(LIVE_DIR, "planet")

MEDIA_ROOT = os.path.join(EXPORT_DIR, "media")

FLATPAGE_IMPORT_DIR = os.path.join(HOME_DIR, "import", "pages")

WHOOSH_INDEX = os.path.join(LIVE_DIR, "whoosh_index")

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': WHOOSH_INDEX,
        'STORAGE': 'file',
        'POST_LIMIT': 128*1024*1024,
        'INCLUDE_SPELLING': True,
        'BATCH-SIZE': 100,
    },
}

PAGINATE_BY = 20

CELERY_CONFIG = 'askcomrade.celeryconfig'

EXTERNAL_LOGIN_URL = None
EXTERNAL_SIGNUP_URL = None
EXTERNAL_LOGOUT_URL = None
EXTERNAL_SESSION_KEY = "EXTERNAL"
EXTERNAL_SESSION_FIELDS = "title tag_val content".split()

COUNT_INTERVAL_WEEKS = 10000

SESSION_UPDATE_SECONDS = 10 * 60
SESSION_COOKIE_NAME = "askcomrade2"

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_KEY = "session"

SITE_LATEST_POST_LIMIT = 6

SITE_STYLE_CSS = "askcomrade.style.less"

COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
)

COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL,
    'SITE_STYLE_CSS': SITE_STYLE_CSS,
}
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Should the django compressor be used.
# USE_COMPRESSOR = False

START_CATEGORIES = [
    "Latest", "Open",
]

NAVBAR_TAGS = [
    "RNA-Seq", "ChIP-Seq", "SNP", "Assembly",
]

END_CATEGORIES = [
    "Tutorials", "Tools", "Jobs", "Forum",
]

# These are the tags that always show up in the tag recommendation dropdown.
POST_TAG_LIST = NAVBAR_TAGS + ["software error"]

# This will form the navbar
CATEGORIES = START_CATEGORIES + NAVBAR_TAGS + END_CATEGORIES

# This will appear as a top banner.
# It should point to a template that will be included.
TOP_BANNER = " haloooooo"

__THIS_DIR = os.path.split(__file__)[0]

__DEFAULT_SITE_DOMAIN = 'www.kipkemei.com'

HOME_DIR = __DEFAULT_HOME


EXPORT_DIR = os.path.join(LIVE_DIR, "export")
WHOOSH_INDEX = os.path.join(LIVE_DIR, "whoosh_index")

ADMIN_NAME = __DEFAULT_ASKCOMRADE_ADMIN_NAME
ADMIN_EMAIL = __DEFAULT_ASKCOMRADE_ADMIN_EMAIL
ADMIN_LOCATION = "Eldoret, KENYA"
ADMINS = (
    (ADMIN_NAME, ADMIN_EMAIL),
)

ASKCOMRADE_VERSION = '1.0.0'
MANAGERS = ADMINS

ATOMIC_REQUESTS = True
CONN_MAX_AGE = 10


LANGUAGE_DETECTION = ['en']

SERVER_EMAIL = DEFAULT_FROM_EMAIL = __DEFAULT_FROM_EMAIL

EMAIL_REPLY_PATTERN = "reply+%s+code@askcomrades.io"

EMAIL_FROM_PATTERN = u'''"%s on Askcomrade" <%s>'''

EMAIL_REPLY_SECRET_KEY = "abc"

EMAIL_REPLY_SUBJECT = u"[askcomrade] %s"

EMAIL_REPLY_REMOVE_QUOTED_TEXT = True

MEDIA_URL = '/static/upload/'

STATIC_URL = '/static/'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


HALF_LIFE = 30.0

LOGIN_REDIRECT_URL = "/"

MESSAGE_TAGS = {
    10: 'alert-info', 20: 'alert-info',
    25: 'alert-success', 30: 'alert-warning', 40: 'alert-danger',
}


CRISPY_TEMPLATE_PACK = 'bootstrap3'


DEBUG_TOOLBAR_PATCH_SETTINGS = False


AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "askcomrade.server.middleware.ExternalAuth",
)

ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# Should the captcha be shown on the signup page.
CAPTCHA = True

# For how long does a user need to be a member to become trusted.
TRUST_RANGE_DAYS = 7

# Votes needed to start trusting the user
TRUST_VOTE_COUNT = 5

# How many non top level posts per day for users.
MAX_POSTS_NEW_USER = 5
MAX_POSTS_TRUSTED_USER = 30

# How many top level posts per day for a new user.
MAX_TOP_POSTS_NEW_USER = 2
MAX_TOP_POSTS_TRUSTED_USER = 5

SOCIALACCOUNT_ADAPTER = 'askcomrade.server.middleware.AutoSignupAdapter'

# Customize this to match the providers listed in the APPs
SOCIALACCOUNT_PROVIDERS ={
    'facebook':
       {'METHOD': 'oauth2',
        'SCOPE': ['email','public_profile', 'user_friends'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time'],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'kr_KR',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.4'
        },

    #
    # 'persona': {
    #     'REQUEST_PARAMETERS': {'siteName': 'Askcomrade'}
    # },
    #
    # 'github': {
    #    'SCOPE': ['email'],
    #    # 'PROVIDER_KEY': get_env("GITHUB_PROVIDER_KEY"),
    #    #  'PROVIDER_SECRET_KEY': get_env("GITHUB_PROVIDER_SECRET_KEY"),
    #    },
    #
    # 'google': {
    #    'SCOPE': ['email', 'https://www.googleapis.com/auth/userinfo.profile'],
    #    'AUTH_PARAMS': {'access_type': 'online'},
    #    # 'PROVIDER_KEY': get_env("GOOGLE_PROVIDER_KEY"),
    #    # 'PROVIDER_SECRET_KEY': get_env("GOOGLE_PROVIDER_SECRET_KEY"),
    # },

}

# The google id will injected as a template variable.
GOOGLE_TRACKER = ""
GOOGLE_DOMAIN = ""

# The site logo.
SITE_LOGO = "askcomrade2.logo.png"

# Digest title
DAILY_DIGEST_TITLE = '[askcomrade daily digest] %s'
WEEKLY_DIGEST_TITLE = '[askcomrade weekly digest] %s'

# The default CSS file to load.
SITE_STYLE_CSS = "askcomrade.style.less"

# Set it to None if all posts should be accesible via the Latest tab.


EXTERNAL_AUTH = [
    ("foo.bar.com", "ABC"),
]

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[askcomrade] "
ACCOUNT_PASSWORD_MIN_LENGHT = 6
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
# ACCOUNT_LOGOUT_ON_GET = True

# Google ReCaptcha No-Captcha settings
# When set the captcha forms will be active.
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""
RECAPTCHA_USE_SSL = True  # Defaults to False
NOCAPTCHA = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# On deployed servers the following must be set.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'deisaack@gmail.com'
EMAIL_HOST_PASSWORD = 'jacktonejacktone'
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# DJANGO_SETTINGS_MODULE = 'askcomrade.settings.base'


ASKCOMRADE_HOSTNAME = "askcomrade.com"

ASKCOMRADE_ADMIN_NAME = "Askcomrade Community"
ASKCOMRADE_ADMIN_EMAIL = "1@lvh.me"

VERBOSITY = 1

PYTHON = "python"

JSON_DATA_FIXTURE = "import/default-fixture.json.gz"

GOOGLE_PROVIDER_KEY = 'key'
GOOGLE_PROVIDER_SECRET_KEY = 'secret'

FACEBOOK_PROVIDER_KEY = 'key'
FACEBOOK_PROVIDER_SECRET_KEY = 'secret'

GITHUB_PROVIDER_KEY = 'key'
GITHUB_PROVIDER_SECRET_KEY = 'secret'

TWITTER_PROVIDER_KEY = 'key'
TWITTER_PROVIDER_SECRET_KEY = 'secret'

ORCID_PROVIDER_KEY = 'key'
ORCID_PROVIDER_SECRET_KEY = 'secret'

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

EMAIL_USE_TLS = True


