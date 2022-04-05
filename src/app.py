import numpy as np
import pandas as pd
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, send_file
import matplotlib.pyplot as plt

from model.src.utils import SIR, run
from model.src.vaccination_strategy.random_strategy import vaccination_strategy as random_vaccination_strategy
from model.src.vaccination_strategy.degree_based_strategy import vaccination_strategy as degree_based_vaccination_strategy
from model.src.vaccination_strategy.occupation_based_strategy import vaccination_strategy as occupation_based_vaccination_strategy

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        return redirect(url_for('prediction'))
    return render_template('index.html')

def make_plot(data, id):

    fig = plt.figure(figsize=(10, 6))

    no_sus = np.array(data['stats']['susceptible'])
    no_inf = np.array(data['stats']['infected'])
    no_rec = np.array(data['stats']['recovered'])
    no_dec = np.array(data['stats']['deceased'])

    time = np.array(range(len(no_sus)))

    plt.plot(time, no_sus, label='Suscepted')
    plt.plot(time, no_inf, label='Infected')
    plt.plot(time, no_rec, label='Recovered')
    plt.plot(time, no_dec, label='Deceased')

    plt.legend()
    plt.tight_layout()
    plt.savefig('assets/' + id + '.jpeg')
    plt.close(fig)

@app.route('/get_assets/<asset_name>')
def get_assets(asset_name):
    return send_file("assets/" + asset_name, attachment_filename = asset_name)

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
    id = "simulation_random"
    vaccinated = random_vaccination_strategy(model)
    output = run(model, vaccinated, 5, id + '.webm')
    full_output[id] = output
    make_plot(full_output[id], id)

    # Degree based Vaccination Strategy
    id = "simulation_degree"
    vaccinated = degree_based_vaccination_strategy(model)
    output = run(model, vaccinated, 5, id + '.webm')
    full_output[id] = output
    make_plot(full_output[id], id)
    
    # Occupation based Vaccination Strategy
    id = "simulation_occupation"
    vaccinated = occupation_based_vaccination_strategy(model)
    output = run(model, vaccinated, 5, id + '.webm')
    full_output[id] = output
    make_plot(full_output[id], id)
    
    return render_template('predict.html', output=full_output)


if __name__ == '__main__':
    app.run(debug=True)
