from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config


# Initialize Application
app = Flask(__name__)
app.config.from_object(Config)


# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)

# Configuration
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes, models
