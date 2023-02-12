from __future__ import division, print_function
import sys
import os
import glob
import re
import numpy as np
import matplotlib.pyplot as plt
import cv2
import tensorflow as tf
from keras.models import load_model
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
#from gevent.wsgi import WSGIServer

app = Flask(__name__)

MODEL_PATH = 'models/PneuCNN.h5'

#Loading the trained model
model = load_model(MODEL_PATH)
print('Model loaded ready to recieve input')



def prediction_model(img_path, model):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224,224))
    if img.shape[2] ==1:
        img = np.dstack([img, img, img])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)/255.
    X = np.expand_dims(img, axis=0)
    X = np.array(X)
    X = tf.convert_to_tensor(X)

    y = model.predict(X, batch_size = 32)
    return y



@app.route('/', methods=['GET'])
def index():
    #default starting web page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        f = request.files['file']
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)


        predictionFromModel = prediction_model(file_path, model)
        os.remove(file_path)
        if predictionFromModel[0]>0.5:
            return("The uploaded image has Pneumonia with {} probability".format(predictionFromModel[0]))
        else:

            return("The uploaded image is Normal with {} probability".format(1-predictionFromModel[0]))
    return None

    
if __name__ == '__main__':
        app.run(port=8000, debug=True)
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()


