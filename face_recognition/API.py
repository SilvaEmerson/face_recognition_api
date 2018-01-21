#-*- encoding: utf-8 -*-

import face_recognition as fr
from flask import Flask, jsonify, request, redirect, render_template
import subprocess as sp
import os
import json

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])

def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            return detect_person(file)

    return  render_template('index.html')

def detect_person(file_name):
    img = fr.load_image_file(file_name)
    img = fr.face_encodings(img)

    if len(img) == 0:
        return "An error hapenned, please choose another picture"

    img = img[0]
    # crie um diretório np root com o nome train contendo
    # as imagens de treino
    know_images = os.listdir('./train')
    #o index 0 escolhe a primeira face da imagem, mas assumindo
    #que existe apenas uma
    know_images_encoded = [fr.face_encodings(fr.load_image_file('./train/' + i))[0] for i in know_images]

    results = fr.compare_faces(know_images_encoded, img)

    if results.count(False) == len(results):
        return "Unknow person"

    result = { i[0]:i[1] for i in zip(results, os.listdir('./train')) }

    #retorna apenas a classe(pessoa) com flag True
    return result[True].rsplit('.', 1)[0]

if __name__ == "__main__":
    port = int(os.enviroment.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
