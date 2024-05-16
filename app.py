from flask import Flask, render_template, request, redirect, url_for, send_file
import random
import pandas as pd
from datetime import datetime
import numpy as np

app = Flask(__name__)

risks = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    risk = {
                        'name': row['Nazwa'],
                        'initial_probability': row['Wzbudzenie [0-1]'],
                        'occurrence_probability': row['Materializacja [0-1]'],
                        'defense_probability': row['Podatnosc [0-1]']
                    }
                    risks.append(risk)
        else:
            name = request.form['name']
            initial_probability = request.form['initial_probability']
            occurrence_probability = request.form['occurrence_probability']
            defense_probability = request.form['defense_probability']

            risk = {
                'name': name,
                'initial_probability': initial_probability,
                'occurrence_probability': occurrence_probability,
                'defense_probability': defense_probability
            }

            risks.append(risk)

    return render_template('index.html', risks=risks)

@app.route('/delete/<int:index>', methods=['POST'])
def delete_risk(index):
    if 0 <= index < len(risks):
        del risks[index]

    return redirect(url_for('index'))

@app.route('/delete_all_risks', methods=['POST'])
def delete_all_risks():
    risks.clear()
    return redirect(url_for('index'))

NUM_OF_ITERATIONS = 1

@app.route('/matrix', methods=['GET'])
def matrix():
    global NUM_OF_ITERATIONS 
    NUM_OF_ITERATIONS = int(request.args.get('iterations', 1))  # Domyślnie 1 iteracja
    risk_matrix = generate_risk_matrix(risks)    
    return render_template('matrix.html', risks=risks, risk_matrix=risk_matrix)

def generate_risk_matrix(risks):
    matrix = {}
    for row in risks:
        matrix[row['name']] = {}
        for col in risks:
            initial_probability = float(row['initial_probability'])
            occurrence_probability = float(col['occurrence_probability'])
            
            matrix[row['name']][col['name']] = round(initial_probability * occurrence_probability, 2)
    return matrix

def choose_danger(potential_dangers, probability_of_potential_dangers_TEST):
    danger = random.choices(potential_dangers, weights=probability_of_potential_dangers_TEST, k=1)[0]
    raised_dangers.append(danger)
    return danger

raised_dangers = []
executed_dangers = []
successful_dangers = []
records = {
}

def execute_danger(starting_danger, potential_dangers_TEST, probability_of_potential_dangers_TEST, relations_between_dangers):
    idx = potential_dangers_TEST.index(starting_danger)
    random_float = random.uniform(0, 1)
    if random_float <= probability_of_potential_dangers_TEST[idx]:
        executed_dangers.append(starting_danger)
        for jdx, value in enumerate(relations_between_dangers[idx]):
            if (jdx != idx) and value == 1:
                raised_dangers.append(potential_dangers_TEST[jdx])
                execute_danger(potential_dangers_TEST[jdx], potential_dangers_TEST, probability_of_potential_dangers_TEST, relations_between_dangers)     

def defense_system(potential_dangers, executed_dangers, probability_of_defense):
    for danger in executed_dangers:
        idx = potential_dangers.index(danger)
        random_float = random.uniform(0, 1)
        if random_float <= probability_of_defense[idx]:
            successful_dangers.append(danger)
            
    key_list = []
    key_list.extend(("Wzbudzone", danger) for danger in raised_dangers)
    key_list.extend(("Wykonane", danger) for danger in executed_dangers)
    key_list.extend(("Sukces", danger) for danger in successful_dangers)
    key = tuple(key_list)
    if key not in records:
        records[key] = 1
    else:
        records[key] += 1

def reset_variables(reset_variables):
    reset_variables.clear()

@app.route('/summary', methods=['GET'])
def summary():

    potential_dangers_TEST = [risk['name'] for risk in risks]
    starting_probability_TEST = [float(risk['initial_probability']) for risk in risks]
    probability_of_potential_dangers_TEST = [float(risk['occurrence_probability']) for risk in risks]
    probability_of_defense_TEST = [float(risk['defense_probability']) for risk in risks]
        
    relations_between_dangers = []
    for risk_row in risks:
        row_values = []
        for risk_col in risks:
            input_name = f"{risk_row['name']}-{risk_col['name']}"
            user_value = float(request.args.get(input_name, 0))
            row_values.append(user_value)
        relations_between_dangers.append(row_values)
    for i in range(NUM_OF_ITERATIONS):
        starting_danger = choose_danger(potential_dangers_TEST, starting_probability_TEST)
        execute_danger(starting_danger, potential_dangers_TEST, probability_of_potential_dangers_TEST, relations_between_dangers)
        defense_system(potential_dangers_TEST, executed_dangers, probability_of_defense_TEST)
        reset_variables(raised_dangers)
        reset_variables(executed_dangers)
        reset_variables(successful_dangers)

    raised_dangers_EXCEL = []
    executed_dangers_EXCEL = []
    successfully_executed_dangers_EXCEL = []
    count = []

    for key, value in records.items():
        local_wzbudzone = []
        local_executed = []
        local_successful = []
        wzbudzone_found = False
        executed_found = False
        success_found = False
        for pair in key:
            if pair[0] == 'Wzbudzone':
                local_wzbudzone.append(pair[1])
                wzbudzone_found = True
            elif pair[0] == 'Wykonane':
                local_executed.append(pair[1])
                executed_found = True
            elif pair[0] == 'Sukces':
                local_successful.append(pair[1])
                success_found = True
        if not wzbudzone_found:
            local_wzbudzone.append('Brak')
        if not executed_found:
            local_executed.append('Brak')
        if not success_found:
            local_successful.append('Brak')
        raised_dangers_EXCEL.append(local_wzbudzone)
        executed_dangers_EXCEL.append(local_executed)
        successfully_executed_dangers_EXCEL.append(local_successful)
        count.append(value)

    df = pd.DataFrame({
        'Wzbudzone zagrożenia': raised_dangers_EXCEL,
        'Materializacja ryzyka': executed_dangers_EXCEL,
        'Obiekt skutecznie naruszony przez zagrożenie (środki ochronne zawiodły)': successfully_executed_dangers_EXCEL,
        'Liczba wystąpień': count
    })
    df = df[df['Materializacja ryzyka'].replace('', np.nan).notna()]
    sum_count = df['Liczba wystąpień'].sum()
    df['Udział procentowy [%]'] = ((df['Liczba wystąpień'] / sum_count) * 100).round(1)
    df = df.sort_values(by='Liczba wystąpień', ascending=False)
    current_time = datetime.now()

    current_time_formatted = current_time.strftime("%Y-%m-%d_%H-%M-%S")

    filename = f'output_{current_time_formatted}.xlsx'
    df.to_excel(filename, index=False)
    # Save DataFrame to Excel with the constructed filename
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
