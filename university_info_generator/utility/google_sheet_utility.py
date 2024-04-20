from typing import Dict, List
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread_dataframe import get_as_dataframe
import pandas
from university_info_generator.configs import config
from .save_load_utility import load_cache
import pandas as pd
import numpy as np


def get_sheet_client(file_path: str = config.CREDENTIAL_JSON_PATH):
    """
    Initializes and returns a gspread client authorized with the specified service account credentials.

    Returns:
        gspread.Client: An authorized gspread client instance.
    """
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    # local contains uforseAdminKey.json
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_path, scope)
    return gspread.authorize(creds)


# Function to check and recreate the sheet if it exists
def recreate_sheet(sheet_client: gspread.Client=get_sheet_client(), title: str="output", spreadsheet_title: str = "working_extract_info_output"):
    """
    Recreates a worksheet within the specified spreadsheet. If a worksheet with the same title exists,
    it is deleted before a new one is created.

    Args:
        sheet_client (gspread.Client): The gspread client instance.
        title (str): The title of the worksheet to recreate.
        spreadsheet_title (str): The title of the spreadsheet where the worksheet resides or will be created.

    Returns:
        gspread.Worksheet: The newly created worksheet object.
    """
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
    sheet_client: gspread.Client,
    cache_column_name: str,
    cache: Dict[str, str],
    spreadsheet_title: str = "working_extract_info_output",
):
    """
    Inserts new rows into a specific worksheet from a provided cache data structure.

    Args:
        sheet_client (gspread.Client): The gspread client instance.
        cache_column_name (str): The key in the cache which holds the data to be inserted.
        cache (dict): A dictionary containing cached data.
        spreadsheet_title (str): The title of the spreadsheet where the data will be inserted.

    Returns:
        None
    """
    new_sheet = recreate_sheet(sheet_client, cache_column_name, spreadsheet_title)
    headers = cache[cache_column_name][0].keys()
    rows = [list(item.values()) for item in cache[cache_column_name]]  # Convert dict values to list
    # Insert headers and rows into the new worksheet
    new_sheet.append_row(list(headers))  # Insert headers
    for row in rows:
        new_sheet.append_row(row)  # Insert each row
    print(f"Data added to '{cache_column_name}' worksheet successfully.")


def get_expect_column(
    sheet_client: gspread.Client = get_sheet_client(),
    spreadsheet_title: str = "working_extract_info_output",
    sheet_title: str = "example_university",
) -> List[str]:
    """
    Retrieves the first row (typically containing column headers) of a worksheet.

    Args:
        sheet_client (gspread.Client): The gspread client instance.
        spreadsheet_title (str): The title of the spreadsheet.
        sheet_title (str): The title of the worksheet from which to retrieve the row.

    Returns:
        list: A list of values from the first row of the worksheet.
    """
    return sheet_client.open(spreadsheet_title).worksheet(sheet_title).row_values(1)


def get_attribute_df(
    sheet_client: gspread.Client = get_sheet_client(),
    spreadsheet_title: str = "working_extract_info_output",
    sheet_title: str = "university_attribute_format",
) -> pandas.DataFrame:
    attribute_sheet = get_worksheet(
        spreadsheet_title=spreadsheet_title, sheet_client=sheet_client, sheetname=sheet_title
    )
    attribute_columns = get_expect_column(
        sheet_client=sheet_client, spreadsheet_title=spreadsheet_title, sheet_title=sheet_title
    )
    return get_as_dataframe(attribute_sheet, evaluate_formulas=True, headers=True, usecols=attribute_columns)


def get_attribute_dict(
    sheet_client: gspread.Client = get_sheet_client(),
    spreadsheet_title: str = "working_extract_info_output",
    sheet_title: str = "university_attribute_format",
) -> Dict[str, Dict[str, str]]:
    df = get_attribute_df(sheet_client, spreadsheet_title, sheet_title)
    df = df.dropna(how="all")  # Clean up the DataFrame
    df.set_index("attribute_name", inplace=True)
    return df.to_dict(orient="index")


def restore_by_cache(cache_file_path, sheet_client: gspread.Client):
    """
    Restores worksheet data from a cache file. For each key in the cache, a worksheet is recreated and
    populated with the cached data.

    Args:
        cache_file_path (str): The path to the cache JSON file.
        sheet_client (gspread.Client): The gspread client instance.

    Returns:
        None
    """
    try:
        with open(cache_file_path, "r", encoding="utf-8") as cache_file:
            cache = json.load(cache_file)
        print("Cache loaded successfully.")
        for key in cache:
            insert_new_rows(sheet_client, key, cache)
    except FileNotFoundError:
        print("Cache file not found. Starting with an empty cache.")
        cache = {}


def get_worksheet(
    spreadsheet_title: str = "working_extract_info_output",
    sheetname: str = "output",
    sheet_client: gspread.Client = get_sheet_client(),
) -> gspread.worksheet:
    """
    Retrieves a specific worksheet by name from the default spreadsheet.

    Args:
        sheetname (str): The name of the worksheet to retrieve.
        sheet_client (gspread.Client): The gspread client instance.

    Returns:
        gspread.Worksheet: The retrieved worksheet object.
    """
    return sheet_client.open(spreadsheet_title).worksheet(sheetname)


def get_worksheet_records(sheet_title: str, sheet_client: gspread.Client = get_sheet_client()):
    """
    Fetches all records from the specified worksheet and returns them as a list of dictionaries.

    Args:
        sheet_title (str): The title of the worksheet from which to fetch records.
        sheet_client (gspread.Client): The gspread client instance.

    Returns:
        dict: A dictionary where the key is the worksheet title and the value is a list of records.
    """
    worksheet = get_worksheet(sheet_title, sheet_client)
    # Fetch all records from the sheet to a list of dictionaries
    records = worksheet.get_all_records()

    # Serialize the list of dictionaries to a JSON string
    return {sheet_title: records}

def clear_worksheet_content(worksheet: gspread.worksheet):
    # Find the number of rows and columns to clear
    all_data = worksheet.get_all_values()
    num_rows = len(all_data)
    num_cols = len(all_data[0]) if num_rows > 0 else 0
    
    # Check if there's more than one row (data rows beyond the header)
    if num_rows > 1:
        # Build the range to clear: starts from row 2 to the last row
        cell_list = worksheet.range('A2:' + gspread.utils.rowcol_to_a1(num_rows, num_cols))
        for cell in cell_list:
            cell.value = ''
        worksheet.update_cells(cell_list)
        print(f"Cleared {num_rows - 1} rows and {num_cols} columns.")


def write_cache_to_worksheet(filepath: str, worksheet: gspread.worksheet):
    try:
        # Load the cached data into a pandas DataFrame
        cache_data = load_cache(filepath)
        
        # If the cached data is a dictionary of dictionaries, convert it to a list of dictionaries
        if isinstance(cache_data, dict):
            cache_data = list(cache_data.values())
        
        # Create a DataFrame from the list of dictionaries
        universities_df = pd.DataFrame(cache_data)
        
        # Cleanse the DataFrame by replacing NaN with empty strings
        universities_df.fillna('', inplace=True)
        
        # Get the headers from the worksheet (assuming the first row is the header)
        headers = worksheet.row_values(1)
        
        # Reorder the DataFrame columns to match the worksheet column order
        # Only include columns that exist in the worksheet; drop any additional columns from the DataFrame
        if set(headers).issubset(set(universities_df.columns)):
            universities_df = universities_df[headers]
        else:
            missing_columns = set(headers) - set(universities_df.columns)
            raise ValueError(f"Missing columns in DataFrame that are expected in the worksheet: {missing_columns}")
        
        # Iterate over DataFrame rows and append each row to the Google Sheet
        for _, row in universities_df.iterrows():
            # Convert all values to string, ensuring proper format for Google Sheets
            row_values = row.astype(str).tolist()
            worksheet.append_row(row_values)
            
    except FileNotFoundError:
        print("Cache file not found. Please ensure the file path is correct.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


__all__ = [name for name in dir() if name[0] != "_"]
