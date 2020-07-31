import datetime
import os

import pytz

from flask_login import LoginManager

login = LoginManager()
login.login_view = 'accounts.login'


def tashkent_now():
    return datetime.datetime.now(pytz.timezone(os.getenv('TZ', 'UTC')))
