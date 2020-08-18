import sys
import logging
import smtplib
import email as em
import configparser

from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from logging.handlers import SMTPHandler, RotatingFileHandler


config = configparser.ConfigParser()
config.read('config.ini')
try:
    flask_secret = config['Flask']['secret']
    email = config['Mail']['email']
    password = config['Mail']['password']
    server = config['Mail']['server']
    port = int(config['Mail']['port'])
    themoviedb_key = config['TheMovieDB']['api_key']
    twitter_oauth = [config['OAuth']['twitter_id'], config['OAuth']['twitter_secret']]
except Exception as e:
    print("Config file error: {}. Please read the README to configure the config.ini file properly.\nExit.".format(e))
    sys.exit()


app = Flask(__name__)
Compress(app)


app.config['SECRET_KEY'] = flask_secret
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True
app.config['MAX_CONTENT_LENGTH'] = 8*1024*1024
app.config['FLASK_ADMIN_SWATCH'] = 'cyborg'

app.config['MAIL_SERVER'] = server
app.config['MAIL_PORT'] = port
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = email
app.config['MAIL_PASSWORD'] = password

app.config['THEMOVIEDB_API_KEY'] = themoviedb_key
app.config['OAUTH_CREDENTIALS'] = {
    'twitter': {
        'id': twitter_oauth[0],
        'secret': twitter_oauth[1]
    }
}


mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
login_manager = LoginManager(app)
login_manager.login_view = 'auth.home'
login_manager.login_message_category = 'info'
app.url_map.strict_slashes = False


from MyLists.auth.routes import bp as auth_bp
app.register_blueprint(auth_bp)

from MyLists.errors.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from MyLists.general.routes import bp as general_bp
app.register_blueprint(general_bp)

from MyLists.main.routes import bp as main_bp
app.register_blueprint(main_bp)

from MyLists.users.routes import bp as users_bp
app.register_blueprint(users_bp)

from MyLists.settings.routes import bp as settings_bp
app.register_blueprint(settings_bp)


if not app.debug and not app.testing:
    class SSLSMTPHandler(SMTPHandler):
        def emit(self, record):
            """ Emit a record. """
            try:
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP_SSL(self.mailhost, port)
                msg = em.message.EmailMessage()
                msg['From'] = self.fromaddr
                msg['To'] = ','.join(self.toaddrs)
                msg['Subject'] = self.getSubject(record)
                msg['Date'] = em.utils.localtime()
                msg.set_content(self.format(record))
                if self.username:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg, self.fromaddr, self.toaddrs)
                smtp.quit()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)
    mail_handler = SSLSMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                  fromaddr=app.config['MAIL_USERNAME'],
                                  toaddrs=app.config['MAIL_USERNAME'],
                                  subject='Mylists - exceptions occurred!',
                                  credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    handler = RotatingFileHandler("MyLists/static/log/mylists.log", maxBytes=10000000, backupCount=5)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.info('MyLists startup')


from MyLists import admin_views
