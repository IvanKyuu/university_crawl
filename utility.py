from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import json
from typing import List


def get_sheet_client(credential_json_file: str = "uforseAdminKey.json"):
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    # local contains uforseAdminKey.json
    creds = ServiceAccountCredentials.from_json_keyfile_name(credential_json_file, scope)
    return gspread.authorize(creds)


# Function to check and recreate the sheet if it exists
def recreate_sheet(sheet_client: gspread.Client, title: str, spreadsheet_title="working_extract_info_output"):
    sheet = sheet_client.open(spreadsheet_title)
    # Check if "title" sheet exists and delete it
    worksheet_list = sheet.worksheets()
    for worksheet in worksheet_list:
        if worksheet.title == title:
            sheet.del_worksheet(worksheet)
            print(f"Worksheet '{title}' found and deleted.")
            break
    sheet.add_worksheet(title=title, rows="100", cols="20")
    print(f"New '{title}' worksheet created.")
    return sheet.worksheet(title)


def insert_new_rows(
    sheet_client: gspread.Client, cache_column_name: str, cache, spreadsheet_title: str = "working_extract_info_output"
):
    new_sheet = recreate_sheet(sheet_client, cache_column_name, spreadsheet_title)
    headers = cache[cache_column_name][0].keys()
    rows = [list(item.values()) for item in cache[cache_column_name]]  # Convert dict values to list
    # Insert headers and rows into the new worksheet
    new_sheet.append_row(list(headers))  # Insert headers
    for row in rows:
        new_sheet.append_row(row)  # Insert each row
    print(f"Data added to '{cache_column_name}' worksheet successfully.")


def load_cache(cache_path):
    with open(cache_path, "r", encoding="utf-8") as cache_file:
        cache = json.load(cache_file)
    return cache


def store_cache(cache_path, cache):
    with open(cache_path, "w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file)


def get_expect_column(
    sheet_client: gspread.Client = get_sheet_client(),
    spreadsheet_title: str = "working_extract_info_output",
    sheet_title: str = "example_university",
):
    return sheet_client.open(spreadsheet_title).worksheet(sheet_title).row_values(1)


def restore_by_cache(cache_file_path, sheet_client: gspread.Client):
    try:
        with open(cache_file_path, "r", encoding="utf-8") as cache_file:
            cache = json.load(cache_file)
        print("Cache loaded successfully.")
        for key in cache:
            insert_new_rows(sheet_client, key, cache)
    except FileNotFoundError:
        print("Cache file not found. Starting with an empty cache.")
        cache = {}


def get_worksheet(sheetname: str, sheet_client: gspread.Client = get_sheet_client()):
    return sheet_client.open("working_extract_info_output").worksheet(sheetname)


def get_worksheet_records(sheet_title: str, sheet_client: gspread.Client = get_sheet_client()):
    worksheet = get_worksheet(sheet_title, sheet_client)
    # Fetch all records from the sheet to a list of dictionaries
    records = worksheet.get_all_records()

    # Serialize the list of dictionaries to a JSON string
    return {sheet_title: records}


def get_expect_column(
    sheet_client: gspread.Client = get_sheet_client(),
    spreadsheet_title: str = "working_extract_info_output",
    sheet_title: str = "example_university",
):
    return sheet_client.open(spreadsheet_title).worksheet(sheet_title).row_values(1)


if __name__ == "__main__":
    cache_repo_path = "./cache_repo"
    restore_by_cache(os.path.join(cache_repo_path, "target_university_before_action.json"), get_sheet_client())
