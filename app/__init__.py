from datetime import datetime
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask, request
from flask_babel import Babel, lazy_gettext as _l
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import current_user
from flask_migrate import Migrate
from flask_moment import Moment
from flask_bootstrap import Bootstrap

from .models import db
from .utils import login
from .views import home_bp, acc_bp

from app import models, common

# init Flask app
app = Flask(__name__, instance_relative_config=True)

# bind blueprints to app
app.register_blueprint(home_bp)
app.register_blueprint(acc_bp)

# Load default config
app.config.from_object('config.default')

# Load config from instance folder
app.config.from_pyfile('config.py')

# Path to .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

# load config from .env
load_dotenv(dotenv_path)
app.config.from_envvar('APP_CONFIG_FILE')

# logger
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')

    handler = RotatingFileHandler('logs/app.log', maxBytes=10240,
                                  backupCount=10)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

# debug toolbar
toolbar = DebugToolbarExtension(app)

# db bind app
db.init_app(app)

# init Migrate
migrate = Migrate(app, db)

# login bind app
login.init_app(app)
login.login_view = 'accounts.login'
login.login_message = _l('Please log in to access this page.')

# init bootstrap
bootstrap = Bootstrap(app)

# init moment.js
moment = Moment(app)

# init Babel
babel = Babel(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': models.User, 'Post': models.Post}


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
