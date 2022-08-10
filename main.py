import datetime

from flask import Flask, redirect, url_for, render_template, request, \
    send_from_directory

from lock_breaker import IMAGE_FILE_NAME, PUZZLE_URL, TEMP
from lock_breaker.gcs import read_encryption_key, update_encryption_key
from lock_breaker.password import encrypt, decrypt
from lock_breaker.rendering import render_text
from lock_breaker.string import text_to_copy
from lock_breaker.validation import input_is_valid

app = Flask(__name__)


@app.route('/')
def index():
    current_time = str(datetime.datetime.now())
    return redirect(url_for(PUZZLE_URL, current_time=current_time))


@app.route(f'/{PUZZLE_URL}/<current_time>', methods=['GET', 'POST'])
def puzzle_for_current_time(current_time):
    text = text_to_copy(current_time)
    render_text(text)
    if request.method == 'GET':
        return render_template('puzzle_for_current_time.html',
                               image_path=url_for('serve_image',
                                                  image_name=IMAGE_FILE_NAME))
    elif request.method == 'POST':
        return handle_encryption_request(text, current_time)


def _impute_empty_string(string: str) -> str:
    if len(string) == 0:
        return '_'
    else:
        return string


def handle_encryption_request(text, current_time):
    copied_text = request.form['text']
    to_decrypt = _impute_empty_string(request.form['decrypt'])
    to_encrypt = _impute_empty_string(request.form['encrypt'])
    if input_is_valid(copied_text, text, current_time):
        code = read_encryption_key()
        return redirect(url_for('password', code=code,
                                to_encrypt=to_encrypt,
                                to_decrypt=to_decrypt))
    else:
        return redirect(url_for('index'))


@app.route(f'/images/<image_name>')
def serve_image(image_name):
    return send_from_directory(TEMP, image_name,
                               as_attachment=True)


@app.route('/password/<code>/<to_encrypt>/<to_decrypt>', methods=['GET', 'POST'])
def password(code, to_encrypt, to_decrypt):
    key = read_encryption_key()
    encrypt_answer = encrypt(to_encrypt, key)
    decrypt_answer = decrypt(to_decrypt, key)
    if request.method == 'GET':
        return render_template('password.html', code=code,
                               encrypt_answer=encrypt_answer,
                               decrypt_answer=decrypt_answer)
    elif request.method == 'POST':
        update_encryption_key()
        code = read_encryption_key()
        return redirect(
            url_for('password', code=code, encrypt_answer=encrypt_answer,
                    decrypt_answer=decrypt_answer))


if __name__ == '__main__':
    app.run(debug=True, port=6006)
