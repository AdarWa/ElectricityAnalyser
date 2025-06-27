# app.py
from flask import Flask, request, render_template, redirect, url_for, request
import os
import analyser
import pandas as pd
from werkzeug.utils import secure_filename
import config

app = Flask(__name__)
UPLOAD_FOLDER = '/config/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            fname = secure_filename(file.filename)
            if not fname:
                return "No file selected", 400
            path = os.path.join(UPLOAD_FOLDER, fname)
            file.save(path)
            return redirect(url_for('results', filename=fname))
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/results/<filename>')
def results(filename):
    filename = secure_filename(filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    df = analyser.open_csv(path)
    grouped_data_period = None
    minPeriod = df['datetime'].min()
    maxPeriod = df['datetime'].max()
    if request.args.get('period_start') and request.args.get('period_end'):
        start_date = pd.to_datetime(request.args.get('period_start', minPeriod.strftime('%d-%m-%Y')), format='%d-%m-%Y').date()
        end_date = pd.to_datetime(request.args.get('period_end', maxPeriod.strftime('%d-%m-%Y')), format='%d-%m-%Y').date()
        df_ = df[(df['datetime'].dt.date >= start_date) & (df['datetime'].dt.date <= end_date)].copy()
        grouped_data_period = analyser.group_by_time(df_)
    else:
        grouped_data_period = analyser.group_by_time(df)
    single_day = request.args.get('single_day', minPeriod.strftime('%d-%m-%Y'))
    try:
        single_date = pd.to_datetime(single_day, format='%d-%m-%Y').date()
        df_ = df[df['datetime'].dt.date == single_date].copy()
        grouped_data_single = analyser.group_by_time(df_).to_dict()
    except ValueError:
        return "Invalid date format. Use DD-MM-YYYY.", 400
    
    plan_results = {}
    price = config.getConfig()["iec_price"]
    plan_prices = {}
    plan_colors = {}
    if request.args.getlist('plan'):
        for plan_name in request.args.getlist('plan'):
            try:
                df_plan = analyser.apply_plan(grouped_data_period.copy(), plan_name)
                df_plan *= price
                plan_prices[plan_name] = round(df_plan.sum(),config.config["rounding_digits"])
                plan_results[plan_name] = df_plan.to_dict()
                plan_colors[plan_name] = next((p for p in config.getConfig()['plans'] if p['name'] == plan_name), None)
            except ValueError as e:
                return str(e), 400
    grouped_data_period = grouped_data_period.to_dict()
    return render_template('results.html', resultsPeriod=grouped_data_period, minPeriod=minPeriod, maxPeriod=maxPeriod, filename=filename, resultsSingle=grouped_data_single, plans=config.getConfig()['plans'], price_without_plan=5, plan_prices=plan_prices, iec_price=config.getConfig()["iec_price"], plan_results=plan_results, plansColors=plan_colors,config=config.config)

@app.route('/config', methods=['GET', 'POST'])
def config_():
    if request.method == 'POST':
        config_content = request.form.get('config_content')
        with open('/config/config.yaml', 'w') as f:
            f.write(config_content)
        config.init()
        return redirect(url_for('config_'))
    with open('/config/config.yaml', 'r') as f:
        config_content = f.read()
    return render_template('config.html', config_content=config_content)

@app.route("/delete/<filename>", methods=["POST"])
def delete_cb(filename):
    filename = secure_filename(filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    else:
        return f"No file named {filename} found.", 400
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000)
