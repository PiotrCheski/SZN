import random
import pandas as pd

potential_dangers_TEST = ["Epidemia", "Powódź"]
starting_probability_TEST = [0.5, 0.5]
probability_of_potential_dangers_TEST = [0.8, 0.9]
probability_of_defense_TEST = [0.8, 0.8]
executed_dangers = []
records = {
}
#######
###E#P#
#E#0#0#
#P#1#0#
#######
relations_between_dangers = [[0,0], [1, 0]]

def choose_danger(potential_dangers, starting_probability):
    danger = random.choices(potential_dangers, probability_of_potential_dangers_TEST, k = 1)
    return danger[0]

def execute_danger(starting_danger, potential_dangers, probability_of_potential_dangers):
    idx = potential_dangers.index(starting_danger)
    random_float = random.uniform(0, 1)
    if random_float <= probability_of_potential_dangers[idx]:
        executed_dangers.append(starting_danger)
        for jdx, value in enumerate(relations_between_dangers[idx]):
            if (jdx != idx) and value == 1:
                execute_danger(potential_dangers[jdx], potential_dangers_TEST, probability_of_potential_dangers_TEST)         
def defense_system(potential_dangers, executed_dangers, probability_of_defense):
    successful_dangers = "Successful dangers: "
    for danger in executed_dangers:
        idx = potential_dangers.index(danger)
        random_float = random.uniform(0, 1)
        if random_float <= probability_of_defense[idx]:
            successful_dangers += f' {danger},'
    key = tuple(executed_dangers + [successful_dangers])
    if key not in records:
        records[key] = 1
    else:
        records[key] += 1

def reset_variables(reset_variables):
    executed_dangers.clear()

def main():
    for i in range(1000):
        print(f'Iteration: {i}')
        starting_danger = choose_danger(potential_dangers_TEST, starting_probability_TEST)
        execute_danger(starting_danger, potential_dangers_TEST, probability_of_potential_dangers_TEST)
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
        'Executed Dangers': executed_dangers_EXCEL,
        'Successfully Executed Dangers': successfully_executed_dangers_EXCEL,
        'Count': count
    })

    # Save the DataFrame to an Excel file
    df.to_excel('output.xlsx', index=False)
if __name__ == "__main__":
    main()