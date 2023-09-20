import datetime

import flask
from flask import Flask, redirect, url_for, render_template, request, \
    send_from_directory, session
from flask_wtf import FlaskForm
from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import Column, String

from flask_login import LoginManager, UserMixin, login_user, login_required

from lock_breaker import IMAGE_FILE_NAME, PUZZLE_URL, TEMP, PUZZLE_START_TIME, \
    PUZZLE_TEXT, MAX_MINUTES_TO_COMPLETE, APP_SECRET_KEY_NAME, PROJECT_ID
from lock_breaker.alchemy import get_engine
from lock_breaker.gcs import read_encryption_key, update_encryption_key, \
    igloo_api_key_writer, igloo_api_key_reader
from lock_breaker.igloo import get_igloo_pins
from lock_breaker.password import encrypt, decrypt
from lock_breaker.rendering import render_text
from lock_breaker.string import text_to_copy
from lock_breaker.time import within_time_limit
from lock_breaker.utility import handle_encryption_request, get_gcp_secret

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = get_gcp_secret(PROJECT_ID, APP_SECRET_KEY_NAME)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialize SQL functionality
engine = get_engine()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base, UserMixin):
    __table_args__ = {'schema': 'user_info'}
    __tablename__ = 'user'
    username = Column(String(50), unique=True, primary_key=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(128))

    def set_password(self, password):
        self.password_hash = sha256_crypt.hash(password)

    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

    def get_id(self):
        return self.username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(username):
    return db_session.query(User).filter_by(username=username).first()

def init_db():
    Base.metadata.create_all(bind=engine)

with app.app_context():
    init_db()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Signup')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            flask.flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html', form=form)


@app.route('/')
@login_required
def index():
    return redirect(url_for(PUZZLE_URL))


def _api_key_exists():
    try:
        _ = igloo_api_key_reader()
        return True
    except:
        return False


@app.route('/igloo_api_key', methods=['GET', 'POST'])
@login_required
def igloo_api_key():
    if request.method == 'GET':
        return render_template('enter_api_key.html')
    elif request.method == 'POST':
        copied_text = request.form['text']
        igloo_api_key_writer(copied_text)
        return redirect(url_for('index'))


@app.route(f'/{PUZZLE_URL}', methods=['GET', 'POST'])
@login_required
def puzzle():
    if request.method == 'GET':
        current_time = str(datetime.datetime.now())
        text = text_to_copy(current_time)
        print(current_time)
        session[PUZZLE_START_TIME] = current_time
        session[PUZZLE_TEXT] = text
        render_text(text)
        if _api_key_exists():
            return render_template('puzzle.html',
                                   image_path=url_for('serve_image',
                                                      image_name=IMAGE_FILE_NAME))
        else:
            return redirect(url_for('igloo_api_key'))
    elif request.method == 'POST':
        copied_text = request.form['text']
        return handle_encryption_request(session[PUZZLE_TEXT],
                                         session[PUZZLE_START_TIME],
                                         copied_text)


@app.route(f'/images/<image_name>')
@login_required
def serve_image(image_name):
    return send_from_directory(TEMP, image_name,
                               as_attachment=True)


@app.route('/password/<code>/<to_encrypt>/<to_decrypt>',
           methods=['GET', 'POST'])
@login_required
def password(code, to_encrypt, to_decrypt):
    key = read_encryption_key()
    estimated_time = decrypt(code, key)
    encrypt_answer = encrypt(to_encrypt, key)
    decrypt_answer = decrypt(to_decrypt, key)
    lock_codes = get_igloo_pins()
    if request.method == 'GET':
        if within_time_limit(estimated_time):
            return render_template('password.html',
                                   encrypt_answer=encrypt_answer,
                                   decrypt_answer=decrypt_answer,
                                   igloo_codes=lock_codes,
                                   time_limit=MAX_MINUTES_TO_COMPLETE)
        else:
            return redirect(url_for('index'))
    elif request.method == 'POST':
        update_encryption_key()
        return redirect(
            url_for('password', code=code, encrypt_answer=encrypt_answer,
                    decrypt_answer=decrypt_answer))

if __name__ == '__main__':
    app.run(port=8080)
