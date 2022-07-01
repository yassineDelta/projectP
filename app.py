#from distutils.util import run_2to3
from flask import Flask, json, jsonify, render_template, request, url_for
#from  optim import opt
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
#Initialize the flask App
import pickle 
import optim
app = Flask(__name__)

model = pickle.load(open('model.pkl', 'rb'))

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/prediction")
def prediction():
    return render_template('prediction.html')

@app.route('/predictionR', methods=['POST','GET'])
def predictionR():
    if request.method == 'POST':
        c1 = request.form['C1']
        c2 = request.form['C2']
        c3 = request.form['C3']
        c4 = request.form['C4']
        c5 = request.form['C5']
        c6 = request.form['C6']
        c7 = request.form['C7']#r4
        c8 = request.form['C8']#r6
        c9 = request.form['C9']#r5
        c10 = request.form['C10'] #r7
        c11 = request.form['C11']
        c12 = request.form['C12']#r8
        r1= (float(c1) * (float(c11)/100)) + (float(c4)* (1-(float(c11)/100)))
        r3= (float(c2) * (float(c11)/100)) + (float(c5)* (1-(float(c11)/100)))
        r2= (float(c3) * (float(c11)/100)) + (float(c6)* (1-(float(c11)/100)))
    input_data = (r1,r2,r3,float(c7),float(c9),float(c8),float(c10),float(c12))
    # change the input data to a numpy array
    input_data_as_numpy_array= np.asarray(input_data)
    # reshape the numpy array as we are predicting for only on instance
    input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)
    value_predicted = model.predict(input_data_reshaped)
       
    #res = value_predicted[0]
    res = value_predicted[0]
    res = float('{:.2f}'.format(float(res)))
    return render_template("predictionR.html",data = res)

@app.route("/optimisation")
def optimisation():
    return render_template('optimisation.html')


@app.route('/optimisationR', methods=['POST','GET'])
def optimisationR():
    if request.method == 'POST':
        c1 = request.form['C1']
        c2 = request.form['C2']
        c3 = request.form['C3']
        c4 = request.form['C4']
        c5 = request.form['C5']
        c6 = request.form['C6']
        c7 = request.form['C7']

        s1 = request.form['s1']
        s2 = request.form['s2']

        s3 = request.form['s3']
        s4 = request.form['s4']

        s5 = request.form['s5']
        s6 = request.form['s6']

        c8 = request.form['C8']
        c9 = request.form['C9']
       
        #res = [0,0,0,0,0,0,0,0,0,0,0,0]
        res = optim.opt(float(c1),float(c2),float(c3),float(c4),float(c5),float(c6),float(c7),float(s1),float(s2),float(s3),float(s4),float(s5),float(s6),float(c8),float(c9))
        return render_template("optimisationR.html",data = res)



if __name__ == "__main__":
    app.run()