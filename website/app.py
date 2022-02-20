import pandas as pd
import os
import io
import random
from flask import Flask, render_template, url_for, request, redirect, Response
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


from utils.utils import SIR, run
from utils.random_strategy import vaccination_strategy


app = Flask(__name__)

class DataStore():
    result = None

data = DataStore()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        metadata = request.files['metadata']
        df = request.files['df']
        filename1 = secure_filename(metadata.filename)
        filename2 = secure_filename(df.filename)
        filepath1 = os.path.join('uploads', filename1)
        metadata.save(filepath1)
        filepath2 = os.path.join('uploads', filename2)
        df.save(filepath2)

        metadata = pd.read_csv(filepath1,sep='\t', lineterminator='\n', names=['ID', 'Class', 'Sex'])
        df = pd.read_csv(filepath2)
        model = SIR(
            metadata=metadata,
            df=df
        )
        vaccinated = vaccination_strategy(model)
        result = run(model,vaccinated,5)
        data.result = result
        return redirect(url_for('prediction', result = result))
    return render_template('index.html')

@app.route('/prediction', methods = ['POST', 'GET'])
def prediction():
    result = request.args['result']
    return render_template('predict.html', result = result)


@app.route('/plot.png')
def plot_png():
    output = data.result
    no_sus = np.array(output['stats']['susceptible'])
    no_inf = np.array(output['stats']['infected'])
    no_rec = np.array(output['stats']['recovered'])
    no_dec = np.array(output['stats']['deceased'])
    time = np.array(range(len(no_sus)))

    fig, axis = plt.subplots(2, 2)
    axis[0,0].plot(time, no_sus)
    axis[0,0].set_title("Suspected")
    
    axis[0,1].plot(time, no_inf)
    axis[0,1].set_title("Infected")

    axis[1,0].plot(time, no_rec)
    axis[1,0].set_title("Recovered")

    axis[1,1].plot(time, no_sus)
    axis[1,1].set_title("Deceased")

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype = 'image/png')

if __name__ == '__main__':
    app.run(debug=True)


