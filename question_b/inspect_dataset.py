import pandas as pd

columns = [
    "age",
    "sex",
    "cp",
    "resting_bp",
    "cholesterol",
    "fbs",
    "restecg",
    "max_hr",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "num",
]

df = pd.read_csv(
    "processed.cleveland.data",
    names=columns,
    na_values="?"
)

print("\nDATASET SHAPE")
print(df.shape)

print("\nFIRST 10 ROWS")
print(df.head(10))

print("\nCOLUMN NAMES")
print(df.columns.tolist())

print("\nMISSING VALUES")
print(df.isnull().sum())

print("\nTARGET DISTRIBUTION")
print(df["num"].value_counts().sort_index())