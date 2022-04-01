import pandas as pd
import os
import random
import sys
from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt


# from utils.utils import SIR, run
# from utils.random_strategy import vaccination_strategy


# sys.path.append('../model')
from model.src.utils import SIR, run
from model.src.vaccination_strategy.random_strategy import random_vaccination_strategy
from model.src.vaccination_strategy.degree_based_strategy import degree_based_vaccination_strategy
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        
        return redirect(url_for('prediction'))
    return render_template('index.html')


@app.route('/prediction')
def prediction():

    metadata = pd.read_csv('model/src/data/generation/metadata.csv')
    df = pd.read_csv('model/src/data/generation/contact_network.csv')
    model = SIR(
        metadata=metadata,
        df=df
    )

    full_output = {}
    # Random Vaccination Strategy
    vaccinated = random_vaccination_strategy(model)
    output = run(model, vaccinated, 5)
    full_output["Random"] = output
    

    # Degree based Vaccination Strategy
    vaccinated = degree_based_vaccination_strategy(model,20,5)
    output = run(model, vaccinated, 5)
    full_output["Degree_based"] = output
    
    return render_template('predict.html', output=full_output)


if __name__ == '__main__':
    app.run(debug=True)
