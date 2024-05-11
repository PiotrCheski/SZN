import itertools
import pandas as pd

def generate_security_combinations(categories, securities):
    combinations = list(itertools.product(*[securities[category] for category in categories]))
    return combinations

categories = ["M1, λ", "M2, λ", "M3, λ", "M4, λ", "M5, λ"]
securities = {
    "M1, λ": ["M1,1", "M1,2"],
    "M2, λ": ["M2,1", "M2,2", "M2,3"],
    "M3, λ": ["M3,1", "M3,2"],
    "M4, λ": ["M4,1", "M4,2"],
    "M5, λ": ["M5,1", "M5,2"]
}

all_combinations = generate_security_combinations(categories, securities)

df = pd.DataFrame(all_combinations, columns=categories)
exclusion_pairs = [["M1,2", "M2,2"], ["M2,3", "M3,1"]]
for pair in exclusion_pairs:
    mask = ((df == pair[0]).sum(axis=1) == 1) & ((df == pair[1]).sum(axis=1) == 1)
    df = df[~mask]

df = df.reset_index(drop=True)
df.index += 1
print(df)
decyzje = [f"Decyzja {i+1}" for i in range(len(df))]

# Wstaw kolumnę "Decyzja" jako pierwszą kolumnę
df.insert(0, "Decyzja", decyzje)

# Ścieżka do pliku Excel
excel_file_path = "combinations.xlsx"

# Zapisz ramkę danych do pliku Excel
df.to_excel(excel_file_path, index=False)

print("Dane zostały zapisane do pliku Excel o nazwie 'combinations.xlsx'.")