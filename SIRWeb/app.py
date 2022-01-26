import pandas as pd
import os
import random
from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt


from utils.utils import SIR, run
from utils.random_strategy import vaccination_strategy


app = Flask(__name__)
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
        return redirect(url_for('prediction', filepath1=filepath1, filepath2= filepath2))
    return render_template('index.html')

@app.route('/prediction')
def prediction():
    filepath1 = request.args['filepath1']
    filepath2 = request.args['filepath2']
    metadata = pd.read_csv(filepath1,sep='\t', lineterminator='\n', names=['ID', 'Class', 'Sex'])
    df = pd.read_csv(filepath2)
    model = SIR(
    metadata=metadata,
    df=df
    )
    vaccinated = vaccination_strategy(model)
    output = run(model,vaccinated,5)
    return render_template('predict.html', output = output)


if __name__ == '__main__':
    app.run(debug=True)


