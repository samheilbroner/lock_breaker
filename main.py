import datetime
from functools import wraps

from flask import Flask, redirect, url_for, render_template, request, \
    send_from_directory, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from passlib.handlers.sha2_crypt import sha256_crypt
from pytz import utc
from werkzeug.middleware.profiler import ProfilerMiddleware
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy.exc import OperationalError
from sqlalchemy import func, exists

from lock_breaker import IMAGE_FILE_NAME, PUZZLE_URL, TEMP, PUZZLE_START_TIME, \
    PUZZLE_TEXT, MAX_MINUTES_TO_COMPLETE, BQ_URI, LOCAL_CREDENTIALS_PATH
from lock_breaker.gcs import read_encryption_key, update_encryption_key, \
    igloo_api_key_writer, igloo_api_key_reader
from lock_breaker.igloo import get_igloo_pins
from lock_breaker.password import encrypt, decrypt
from lock_breaker.rendering import render_text
from lock_breaker.string import text_to_copy
from lock_breaker.time import within_time_limit
from lock_breaker.validation import input_is_valid

from google.oauth2.service_account import Credentials

credentials = Credentials.from_service_account_file(LOCAL_CREDENTIALS_PATH)

app = Flask(__name__)

app.secret_key = 'aslkfjfdsoi49'
app.config['SQLALCHEMY_DATABASE_URI'] = BQ_URI
db = SQLAlchemy(app)

def table_has_rows(db, table):
    try:
        return db.session.query(exists().select_from(table)).scalar()
    except OperationalError:
        return False

class User(db.Model):
    username = db.Column(db.String(50), unique=True, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = sha256_crypt.hash(password)

    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

    __table_args__ = {'schema': 'lock_breaker'}

with app.app_context():
    db.create_all()

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Signup')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if logged in and username has not expired
        if 'username' in session:
            expiration_time = session['username_expiration'].replace(tzinfo=datetime.timezone.utc)
            current_time = datetime.datetime.now(datetime.timezone.utc)

            print(expiration_time)
            print(current_time)

            if expiration_time > current_time:
                return f(*args, **kwargs)

        flash("You need to be logged in to access this page.", "warning")
        return redirect(url_for('login'))

    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            session['username'] = form.username.data
            session['username_expiration'] = datetime.datetime.now(tz=datetime.timezone.utc) + \
                                             datetime.timedelta(minutes=30)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)
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


def _impute_empty_string(string: str) -> str:
    if len(string) == 0:
        return '_'
    else:
        return string


def handle_encryption_request(text, current_time, copied_text):
    to_decrypt = _impute_empty_string(request.form['decrypt'])
    to_encrypt = _impute_empty_string(request.form['encrypt'])
    key = read_encryption_key()
    code = encrypt(current_time, key)
    if input_is_valid(copied_text, text, current_time):
        return redirect(url_for('password',
                                code=code,
                                to_encrypt=to_encrypt,
                                to_decrypt=to_decrypt))
    else:
        return redirect(url_for('index'))


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
    app.run(debug=True, port=8080)
