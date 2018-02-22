#-*- encoding: utf-8 -*-

import face_recognition as fr
from flask import Flask, jsonify, request, redirect, render_template
from werkzeug.utils import secure_filename
import os
import json
import numpy as np
import requests

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'npy'}
UPLOAD_FOLDER = './root/face_recognition/static/train'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#manage file
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_person(file_name):
    img = fr.load_image_file(file_name)
    img = fr.face_encodings(img)

    # crie um diretório no root com o nome train contendo
    # as imagens de treino
    know_images = os.listdir('./root/face_recognition/static/train')

    know_images_encoded = [np.load('./root/face_recognition/static/train/' + i) for i in know_images]
    # know_images_encoded = [fr.face_encodings(fr.load_image_file('./root/face_recognition/static/train/' + i))[0] for i in know_images]

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

        return jsonify([{"response": results}])

    img = img[0]
    results = fr.compare_faces(know_images_encoded, img)

    if results.count(False) == len(results):
        return jsonify([{"response": "Unknow person"}])

    result = { i[0]:i[1] for i in zip(results, os.listdir('./root/face_recognition/static/train')) }

    #retorna apenas a classe(pessoa) com flag True
    return jsonify([{"response": result[True].rsplit('.', 1)[0]}])


def send_file(path):
    url = "https://api.cloudinary.com/v1_1/silvaemerson/image/upload"

    jsonData = {}

    #open file
    files = {'file': open(path, 'rb')}
    values = {'upload_preset': 'train_set'}

    #send file
    response = requests.post(url, files=files, data=values)
    print("\n\nStatus: " + str(response.status_code) + "\n\n")
    if(response.status_code == 200):
        jsonData = json.loads(response.text)
        print(jsonData)

    return jsonData

#resources
@app.route('/images', methods=['GET'])
def get_filenames():
    if request.method == 'GET':
        filename = [name.rsplit('.', 1)[0] for name in os.listdir("./root/face_recognition/static/train/")]

        return jsonify([{"filenames": filename}])


@app.route('/upload_image', methods=['GET', 'POST'])
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

            #save file
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_path)

            #load face
            img = fr.load_image_file('./root/face_recognition/static/train/%s'%filename)
            img = fr.face_encodings(img)

            #save only face, if has more than one, don't will save it
            if len(img) == 0 or len(img) >= 2:
                os.system('rm ./root/face_recognition/static/train/%s' % filename)
                return "An error happened, please choose another picture"

            #send image to Cloudinary
            send_file(saved_path)

            #delete image
            os.system('rm ./root/face_recognition/static/train/%s' % filename)

            #save encode of image
            np.save('./root/face_recognition/static/train/%s'%filename.rsplit('.', 1)[0], img[0])
            return "Upload completed"

    return  render_template('add-image-template.html')


@app.route('/delete_image/<string:filename>', methods=['DELETE'])
def delete_image(filename):
    if request.method == 'DELETE':

        # filename = request.args.get('filename')
        filename = secure_filename(filename)

        if(filename != ""):
            files = [name.rsplit('.', 1)[0] for name in os.listdir("./root/face_recognition/static/train/")]

            exists = False

            for name in files:
                if(name == filename):
                    exists = True

            if exists:
                os.system('rm ./root/face_recognition/static/train/%s.*' % filename)
                return jsonify([{"response": "Removed"}])

            else:
                return jsonify([{"response": "Not removed"}])

        else:
            return "An error happened, please choose a filename"

    #Old version

    # if(request.is_json):
    #
    #     content = request.get_json()
    #     filename = content['filename'].rsplit('.', 1)[0]
    #
    #     if(filename != ""):
    #         files = [name.rsplit('.', 1)[0] for name in os.listdir("./root/face_recognition/static/train/")]
    #
    #         exists = False
    #
    #         for name in files:
    #             if(name == filename):
    #                 exists = True
    #
    #         if exists:
    #             os.system('rm ./root/face_recognition/static/train/%s.*' % filename)
    #             return jsonify([{"response": "Removed"}])
    #
    #         else:
    #             return jsonify([{"response": "Not removed"}])
    #
    #     else:
    #         return "An error happened, please choose a filename"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
