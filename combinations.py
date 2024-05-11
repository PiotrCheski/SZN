import itertools
import pandas as pd

def generate_security_combinations(categories, securities):
    combinations = list(itertools.product(*[securities[category] for category in categories]))
    return combinations

categories = ["Z2,1", "Z2,2", "Z2,3"]
securities = {
    "Z2,1": ["M2,1,1", "M2,1,2", "M2,1,3"],
    "Z2,2": ["M2,2,1", "M2,2,2"],
    "Z2,3": ["M2,3,1", "M2,3,2"]
}

all_combinations = generate_security_combinations(categories, securities)

df = pd.DataFrame(all_combinations, columns=categories)

exclusion_pairs = [["M2,1,2", "M2,2,1"], ["M2,1,3", "M2,3,1"]]
for pair in exclusion_pairs:
    mask = ((df == pair[0]).sum(axis=1) == 1) & ((df == pair[1]).sum(axis=1) == 1)
    df = df[~mask]

print(df)
