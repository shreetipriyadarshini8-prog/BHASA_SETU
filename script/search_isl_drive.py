# -*- coding: utf-8 -*-
"""
BHASA SETU
Step 2 - Search ISL Dictionary for Patient Phrases
"""

import os
import re
import time
import pandas as pd

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATIENT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "patient_phrases.csv"
)

FOLDER_FILE = os.path.join(
    BASE_DIR,
    "data",
    "isl_dictionary_folders.csv"
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "credentials",
    "token.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "csv",
    "isl_mapping.csv"
)

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

# =========================================================
# GOOGLE DRIVE
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly"
]


# =========================================================
# START
# =========================================================

print("=" * 65)
print("       BHASA SETU - ISL PHRASE SEARCH")
print("=" * 65)


# =========================================================
# CHECK FILES
# =========================================================

for file_path in [
    PATIENT_FILE,
    FOLDER_FILE,
    TOKEN_FILE
]:

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"\nRequired file not found:\n{file_path}"
        )


print("\nRequired files found. ✅")


# =========================================================
# LOAD PATIENT DATA
# =========================================================

patient_df = pd.read_csv(
    PATIENT_FILE
)

print(
    "\nPatient phrases loaded:",
    len(patient_df)
)

print("\nColumns found:")

print(
    patient_df.columns.tolist()
)


# =========================================================
# LOAD ISL FOLDERS
# =========================================================

folder_df = pd.read_csv(
    FOLDER_FILE
)

print(
    "\nISL dictionary folders:",
    len(folder_df)
)


# =========================================================
# GOOGLE AUTH
# =========================================================

print("\nConnecting to Google Drive...")

creds = Credentials.from_authorized_user_file(
    TOKEN_FILE,
    SCOPES
)

service = build(
    "drive",
    "v3",
    credentials=creds
)

print("Google Drive connected. ✅")


# =========================================================
# FIND ALL DICTIONARY FOLDER
# =========================================================

all_folder = folder_df[
    folder_df["folder_name"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "all dictionary videos"
]


if all_folder.empty:

    raise RuntimeError(
        "All Dictionary Videos folder not found."
    )


all_url = str(
    all_folder.iloc[0]["drive_url"]
)


match = re.search(
    r"/folders/([a-zA-Z0-9_-]+)",
    all_url
)


if not match:

    raise RuntimeError(
        "Could not extract All Dictionary Videos folder ID."
    )


ROOT_FOLDER_ID = match.group(1)

print(
    "\nRoot ISL folder:",
    ROOT_FOLDER_ID
)


# =========================================================
# DRIVE SEARCH FUNCTION
# =========================================================

def search_drive(query):

    results = []

    page_token = None

    while True:

        response = service.files().list(
            q=query,
            spaces="drive",
            fields=(
                "nextPageToken,"
                "files("
                "id,"
                "name,"
                "mimeType,"
                "parents,"
                "webViewLink"
                ")"
            ),
            pageSize=100,
            pageToken=page_token
        ).execute()

        results.extend(
            response.get("files", [])
        )

        page_token = response.get(
            "nextPageToken"
        )

        if not page_token:
            break

    return results


# =========================================================
# RECURSIVE FOLDER SEARCH
# =========================================================

def get_all_files(folder_id):

    all_files = []

    queue = [
        folder_id
    ]

    visited = set()

    while queue:

        current_folder = queue.pop(0)

        if current_folder in visited:
            continue

        visited.add(current_folder)

        print(
            "Scanning folder:",
            current_folder
        )

        query = (
            f"'{current_folder}' in parents "
            "and trashed = false"
        )

        files = search_drive(query)

        for file in files:

            mime = file.get(
                "mimeType",
                ""
            )

            if mime == "application/vnd.google-apps.folder":

                queue.append(
                    file["id"]
                )

            else:

                all_files.append(file)

    return all_files


# =========================================================
# GET DICTIONARY FILES
# =========================================================

print("\nSearching dictionary recursively...")
print("This may take some time because the dictionary is large.")
print("Please don't stop Spyder while it is scanning.\n")


dictionary_files = get_all_files(
    ROOT_FOLDER_ID
)


print(
    "\nTotal dictionary files found:",
    len(dictionary_files)
)


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize(text):

    text = str(text).lower()

    text = text.replace(
        "_",
        " "
    )

    text = text.replace(
        "-",
        " "
    )

    text = re.sub(
        r"[^a-z0-9 ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# SEARCH TERM GENERATOR
# =========================================================

def generate_terms(row):

    terms = []

    possible_columns = [
        "phrase_key",
        "patient_phrase",
        "english",
        "phrase",
        "text"
    ]

    for column in possible_columns:

        if column in row.index:

            value = row[column]

            if pd.notna(value):

                value = str(value).strip()

                if value:

                    terms.append(
                        value
                    )

    # Add normalized versions
    expanded = []

    for term in terms:

        expanded.append(
            term
        )

        normalized = normalize(
            term
        )

        if normalized:

            expanded.append(
                normalized
            )

            words = normalized.split()

            for word in words:

                if len(word) >= 3:

                    expanded.append(
                        word
                    )

    # Remove duplicates
    final_terms = []

    seen = set()

    for term in expanded:

        key = normalize(term)

        if key and key not in seen:

            seen.add(key)

            final_terms.append(
                key
            )

    return final_terms


# =========================================================
# SEARCH EACH PATIENT PHRASE
# =========================================================

mapping = []

total_phrases = len(
    patient_df
)


for index, row in patient_df.iterrows():

    phrase_number = index + 1

    print(
        f"\n[{phrase_number}/{total_phrases}] Searching..."
    )

    terms = generate_terms(
        row
    )

    print(
        "Search terms:",
        terms
    )


    # -----------------------------------------------------
    # Get phrase information
    # -----------------------------------------------------

    phrase_key = ""

    patient_phrase = ""

    if "phrase_key" in row.index:

        phrase_key = str(
            row["phrase_key"]
        )

    elif "key" in row.index:

        phrase_key = str(
            row["key"]
        )


    if "patient_phrase" in row.index:

        patient_phrase = str(
            row["patient_phrase"]
        )

    elif "english" in row.index:

        patient_phrase = str(
            row["english"]
        )

    elif "phrase" in row.index:

        patient_phrase = str(
            row["phrase"]
        )


   # =========================================================
# SEARCH EACH PATIENT PHRASE
# =========================================================

mapping = []

total_phrases = len(patient_df)

for index, row in patient_df.iterrows():

    phrase_number = index + 1

    print(
        f"\n[{phrase_number}/{total_phrases}] Searching..."
    )

    terms = generate_terms(row)

    print(
        "Search terms:",
        terms
    )

    # -----------------------------------------------------
    # Get phrase information
    # -----------------------------------------------------

    phrase_key = ""

    patient_phrase = ""

    if "phrase_key" in row.index:
        phrase_key = str(row["phrase_key"])

    elif "key" in row.index:
        phrase_key = str(row["key"])

    if "patient_phrase" in row.index:
        patient_phrase = str(row["patient_phrase"])

    elif "english" in row.index:
        patient_phrase = str(row["english"])

    elif "phrase" in row.index:
        patient_phrase = str(row["phrase"])

    # -----------------------------------------------------
    # Search dictionary files
    # -----------------------------------------------------

    found = []

    found_ids = set()

    for file in dictionary_files:

        filename = normalize(
            file.get("name", "")
        )

        for term in terms:

            if term in filename:

                file_id = file.get("id")

                if file_id not in found_ids:

                    found_ids.add(file_id)

                    if filename == term:

                        match_type = "EXACT"

                    else:

                        match_type = "PARTIAL"

                    found.append({
                        "file": file,
                        "term": term,
                        "match_type": match_type
                    })

    # -----------------------------------------------------
    # Save matches
    # -----------------------------------------------------

    if found:

        for item in found:

            file = item["file"]

            mapping.append({

                "phrase_key":
                    phrase_key,

                "patient_phrase":
                    patient_phrase,

                "search_term":
                    item["term"],

                "match_type":
                    item["match_type"],

                "video_name":
                    file.get(
                        "name",
                        ""
                    ),

                "video_id":
                    file.get(
                        "id",
                        ""
                    ),

                "mime_type":
                    file.get(
                        "mimeType",
                        ""
                    ),

                "drive_url":
                    (
                        "https://drive.google.com/"
                        "file/d/"
                        + file.get(
                            "id",
                            ""
                        )
                        + "/view"
                    )
            })

    else:

        mapping.append({

            "phrase_key":
                phrase_key,

            "patient_phrase":
                patient_phrase,

            "search_term":
                "",

            "match_type":
                "NOT_FOUND",

            "video_name":
                "",

            "video_id":
                "",

            "mime_type":
                "",

            "drive_url":
                ""
        })


# =========================================================
# SAVE MAPPING
# =========================================================

mapping_df = pd.DataFrame(mapping)

mapping_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# SUMMARY
# =========================================================

print("\n")
print("=" * 65)
print("                  SEARCH COMPLETE")
print("=" * 65)

print("\nMapping file created:")

print(OUTPUT_FILE)

print(
    "\nTotal mapping rows:",
    len(mapping_df)
)

print("\nMatch summary:")

print(
    mapping_df[
        "match_type"
    ].value_counts()
)

print("\n" + "=" * 65)
print("DONE")
print("=" * 65)