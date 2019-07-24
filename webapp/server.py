#python3 server.py "image_name"

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import numpy as np
from PIL import Image
import segment
from datetime import datetime
import os
import string
import random

SAVE_DIR = "./images"
if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)

app = Flask(__name__, static_url_path="")

def random_str(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])

@app.route('/')
def index():
    return render_template('index.html', images=os.listdir(SAVE_DIR)[::-1])

@app.route('/images/<path:path>')
def send_js(path):
    return send_from_directory(SAVE_DIR, path)

@app.route('/upload', methods=['POST'])
def upload():
    if request.files['image']:
        # gazou yomikomi
        stream = request.files['image'].stream
        img_array = Image.open(stream)
        # henkan
        img = segment.segment(img_array)
        # hozon
        dt_now = datetime.now().strftime("%Y_%m_%d%_H_%M_%S_") + random_str(5)
        save_path = os.path.join(SAVE_DIR, dt_now + ".png")
        img.save(save_path)
        print("save", save_path)
        return redirect('/')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8888)
