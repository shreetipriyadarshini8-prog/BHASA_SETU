import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

targets = {
    "shivering",
    "getting_worse",
    "started_suddenly",
    "started_slowly",
    "pregnant",
    "fainted"
}

print("=" * 80)
print("BHASA SETU — FIND CUSTOM MAPPINGS")
print("=" * 80)

for root, dirs, files in os.walk(BASE):

    # Don't inspect credentials
    if "credentials" in root.lower():
        continue

    for file in files:

        if not file.lower().endswith(".csv"):
            continue

        path = os.path.join(root, file)

        try:
            df = pd.read_csv(path)

            if "phrase_key" not in df.columns:
                continue

            found = df[df["phrase_key"].astype(str).isin(targets)]

            if len(found) > 0:
                print("\n" + "=" * 80)
                print("FILE FOUND:")
                print(path)
                print("=" * 80)

                print(
                    found.to_string(index=False)
                )

        except Exception:
            pass

print("\n" + "=" * 80)
print("SEARCH COMPLETE")
print("=" * 80)