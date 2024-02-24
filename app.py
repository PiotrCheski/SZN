import random
potential_dangers_TEST = ["Epidemia", "Powódź"]
starting_probability_TEST = [0.2, 0.8]
probability_of_potential_dangers_TEST = [0.9, 0.9]
already_used_dangers = []
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
    print(starting_danger)
    if random_float <= probability_of_potential_dangers[idx]:
        other_dangers = []
        for jdx, value in enumerate(relations_between_dangers[idx]):
            if (jdx != idx) and value == 1:
                other_dangers.append(potential_dangers[jdx])
        print(f'Other dangers: {other_dangers}')
    else:
        print("You are safe")

def main():
    starting_danger = choose_danger(potential_dangers_TEST, starting_probability_TEST)
    execute_danger(starting_danger, potential_dangers_TEST, probability_of_potential_dangers_TEST)

if __name__ == "__main__":
    main()