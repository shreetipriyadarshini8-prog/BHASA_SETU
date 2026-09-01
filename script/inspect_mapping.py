import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mapping_file = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_clean.csv")

df = pd.read_csv(mapping_file, encoding="utf-8-sig")

print("=" * 60)
print("ISL MAPPING CLEAN — INSPECTION")
print("=" * 60)

print("\nNumber of rows:", len(df))

print("\nColumns:")
for col in df.columns:
    print(" -", col)

print("\nFirst 10 rows:")
print(df.head(10).to_string(index=False))

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("=" * 60)