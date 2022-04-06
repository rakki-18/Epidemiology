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
    # if request.method == "POST":
    # return redirect(url_for('prediction'))
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

    plt.legend(fontsize=20)
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
    
    # Comparison of Vaccination Strategies with the help of a Bar Chart
    y1 = [max(full_output[id]['stats']['infected']) 
        for id in ['simulation_random','simulation_degree','simulation_occupation']]
    y2 = [max(full_output[id]['stats']['recovered']) 
        for id in ['simulation_random','simulation_degree','simulation_occupation']]
    y3 = [max(full_output[id]['stats']['deceased']) 
        for id in ['simulation_random','simulation_degree','simulation_occupation']]
    
    df = pd.DataFrame([['Infected']+y1, ['Recovered']+y2, ['Deceased']+y3],
                columns=['Compartments', 'Random Strategy', 'Degree Based', 'Occupation Based'])
    plot=df.plot(x='Compartments', kind='bar',stacked=False, 
                    title='Comparison of Vaccination Strategies', rot=0, figsize=(25, 12), fontsize=20)
    plot.legend(fontsize=25)
    plot.set_xlabel('Compartments',fontdict={'fontsize':25})
    plot.set_title('Comparison of Vaccination Strategies', fontdict={'fontsize':30})
    fig=plot.get_figure()
    fig.savefig('assets/comparison_graph.jpeg')
    
    return render_template('index.html', output=full_output)


if __name__ == '__main__':
    app.run(debug=True)
