from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd
from datetime import datetime
import numpy as np

app = Flask(__name__)

risks = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:  # Sprawdzenie, czy przesłano plik
            file = request.files['file']
            if file.filename != '':
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    risk = {
                        'name': row['A'],
                        'initial_probability': row['B'],
                        'occurrence_probability': row['C'],
                        'defense_probability': row['D']
                    }
                    risks.append(risk)
        else:  # Jeśli dane zostały przesłane przez formularz
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

@app.route('/matrix', methods=['GET'])
def matrix():
    risk_matrix = generate_risk_matrix(risks)    
    return render_template('matrix.html', risks=risks, risk_matrix=risk_matrix)

def generate_risk_matrix(risks):
    matrix = {}
    for row in risks:
        matrix[row['name']] = {}
        for col in risks:
            # Convert probability values to floats
            initial_probability = float(row['initial_probability'])
            occurrence_probability = float(col['occurrence_probability'])
            
            # Compute the combination of probabilities (customize this according to your needs)
            matrix[row['name']][col['name']] = round(initial_probability * occurrence_probability, 2)
    return matrix


def choose_danger(potential_dangers, probability_of_potential_dangers_TEST):
    danger = random.choices(potential_dangers, probability_of_potential_dangers_TEST, k = 1)
    return danger[0]


executed_dangers = []
records = {
}

def execute_danger(starting_danger, potential_dangers_TEST, probability_of_potential_dangers_TEST, relations_between_dangers):
    idx = potential_dangers_TEST.index(starting_danger)
    random_float = random.uniform(0, 1)
    if random_float <= probability_of_potential_dangers_TEST[idx]:
        executed_dangers.append(starting_danger)
        for jdx, value in enumerate(relations_between_dangers[idx]):
            if (jdx != idx) and value == 1:
                execute_danger(potential_dangers_TEST[jdx], potential_dangers_TEST, probability_of_potential_dangers_TEST, relations_between_dangers)     

def defense_system(potential_dangers, executed_dangers, probability_of_defense):
    successful_dangers = ""
    for danger in executed_dangers:
        idx = potential_dangers.index(danger)
        random_float = random.uniform(0, 1)
        if random_float >= probability_of_defense[idx]:
            successful_dangers += f' {danger},'
    key = tuple(executed_dangers + [successful_dangers])
    if key not in records:
        records[key] = 1
    else:
        records[key] += 1

def reset_variables(reset_variables):
    executed_dangers.clear()

@app.route('/summary', methods=['GET'])
def summary():

    potential_dangers_TEST = [risk['name'] for risk in risks]
    starting_probability_TEST = [float(risk['initial_probability']) for risk in risks]
    probability_of_potential_dangers_TEST = [float(risk['occurrence_probability']) for risk in risks]
    probability_of_defense_TEST = [float(risk['defense_probability']) for risk in risks]
        
    # Fetch relations_between_dangers from the form data (example structure)
    # You may need to adjust this based on the actual structure of your data
    relations_between_dangers = []
    for risk_row in risks:
        row_values = []
        for risk_col in risks:
            input_name = f"{risk_row['name']}-{risk_col['name']}"
            user_value = float(request.args.get(input_name, 0))
            row_values.append(user_value)
        relations_between_dangers.append(row_values)
    for i in range(10000):
        starting_danger = choose_danger(potential_dangers_TEST, starting_probability_TEST)
        execute_danger(starting_danger, potential_dangers_TEST, probability_of_potential_dangers_TEST, relations_between_dangers)
        defense_system(potential_dangers_TEST, executed_dangers, probability_of_defense_TEST)
        reset_variables(executed_dangers)
       # Extract information from the keys
    executed_dangers_EXCEL = []
    successfully_executed_dangers_EXCEL = []
    count = []

    for key, value in records.items():
        executed_dangers_EXCEL.append(', '.join(key[:-1]))  # Exclude the last element
        successfully_executed_dangers_EXCEL.append(', '.join(key[-1].split(', ')))  # Split the string and join back with commas
        count.append(value)
    
    # Create a DataFrame
    df = pd.DataFrame({
        'Materializacja ryzyka': executed_dangers_EXCEL,
        'Obiekt skutecznie naruszony przez zagrożenie (środki ochronne zawiodły)': successfully_executed_dangers_EXCEL,
        'Liczba wystąpień': count
    })
    df = df[df['Materializacja ryzyka'].replace('', np.nan).notna()]
    sum_count = df['Liczba wystąpień'].sum()
    df['Udział procentowy [%]'] = ((df['Liczba wystąpień'] / sum_count) * 100).round(1)
    df = df.sort_values(by='Liczba wystąpień', ascending=False)
    # Get current time
    current_time = datetime.now()

    # Format current time to include hour and seconds
    current_time_formatted = current_time.strftime("%Y-%m-%d_%H-%M-%S")

    # Construct filename with current time
    filename = f'output_{current_time_formatted}.xlsx'

    # Save DataFrame to Excel with the constructed filename
    df.to_excel(filename, index=False)
    
    return render_template('summary.html')

 


if __name__ == '__main__':
    app.run(debug=True)
