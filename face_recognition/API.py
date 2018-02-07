#-*- encoding: utf-8 -*-

import face_recognition as fr
from flask import Flask, jsonify, request, redirect, render_template
from werkzeug.utils import secure_filename
import os
import json

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt'}
UPLOAD_FOLDER = './static/train'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

    # crie um diretório np root com o nome train contendo
    # as imagens de treino
    know_images = os.listdir('./static/train')
    #o index 0 escolhe a primeira face da imagem, mas assumindo
    #que existe apenas uma
    know_images_encoded = [fr.face_encodings(fr.load_image_file('./static/train/' + i))[0] for i in know_images]

    if len(img) == 0:
        return jsonify([{"response": "An error hapenned, please choose another picture"}])
    elif len(img) > 1:
        know_images_names = [i.rsplit('.', 1)[0] for i in know_images]
        results = []
        for i in img:
            matches = fr.compare_faces(know_images_encoded, i)
            name = "Unknow person"

            if True in matches:
                first_match_index = matches.index(True)
                name = know_images_names[first_match_index]

            results.append(name)

        return jsonify([{"result": results}])

    img = img[0]
    results = fr.compare_faces(know_images_encoded, img)

    if results.count(False) == len(results):
        return jsonify([{"response": "Unknow person"}])

    result = { i[0]:i[1] for i in zip(results, os.listdir('./static/train')) }

    #retorna apenas a classe(pessoa) com flag True
    return jsonify([{"response": result[True].rsplit('.', 1)[0]}])


@app.route('/add_image', methods=['GET', 'POST'])

def add_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_path)

            img = fr.load_image_file('./static/train/%s'%filename)
            img = fr.face_encodings(img)

            if len(img) == 0:
                os.system('rm ./static/train/%s'%filename)
                return "An error hapenned, please choose another picture"

            return "Upload completed"

    return  render_template('add-image-template.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
