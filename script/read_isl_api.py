# -*- coding: utf-8 -*-
"""
Bhasa Setu
Step 1 - Read ISL Dictionary XML
"""

import os
import pandas as pd
import xml.etree.ElementTree as ET

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

XML_FILE = os.path.join(
    BASE_DIR,
    "data",
    "isl_dictionary.xml"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "isl_dictionary_folders.csv"
)

# ---------------------------------------------------------
# CHECK XML FILE
# ---------------------------------------------------------

if not os.path.exists(XML_FILE):
    print("ERROR: XML file not found!")
    print(XML_FILE)
    raise FileNotFoundError(XML_FILE)

print("=" * 55)
print("        BHASA SETU - ISL DICTIONARY READER")
print("=" * 55)

print("\nXML file:")
print(XML_FILE)

# ---------------------------------------------------------
# READ XML
# ---------------------------------------------------------

tree = ET.parse(XML_FILE)
root = tree.getroot()

print("\nXML loaded successfully.")

# ---------------------------------------------------------
# FIND RECORDS
# ---------------------------------------------------------

records = []

for elem in root.iter():

    folder_name = None
    link = None

    for child in elem:

        tag = child.tag.lower()

        if "folder_name" in tag:
            folder_name = child.text

        elif tag == "link_" or "link_" in tag:
            link = child.text

    if folder_name and link:

        records.append({
            "folder_name": folder_name.strip(),
            "drive_url": link.strip()
        })

# ---------------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------------

df = pd.DataFrame(records)

if df.empty:
    print("\nWARNING: No folder records were found.")
else:

    df = df.drop_duplicates()

    # -----------------------------------------------------
    # SAVE CSV
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nFolders found:", len(df))

    print("\n---------------------------------------")
    print("ISL DICTIONARY FOLDERS")
    print("---------------------------------------")

    print(df.to_string(index=False))

    print("\n---------------------------------------")
    print("Saved successfully:")
    print(OUTPUT_FILE)

print("\nDone.")