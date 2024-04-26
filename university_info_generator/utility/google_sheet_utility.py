"""
This module provides utilities for managing data interaction between Google Sheets and a local cache system.
It leverages the `gspread` library to manipulate Google Sheets, enabling CRUD operations on sheet data.
The module facilitates the loading and storing of data, the creation and management of worksheets,
    and the handling of cache data to synchronize with Google Sheets.

Key functionalities include:
- Authorizing a gspread client using service account credentials.
- Recreating a worksheet to ensure fresh data setup.
- Inserting new rows into a worksheet from cached data.
- Fetching and formatting data from specific worksheets.
- Clearing worksheet content while preserving headers.
- Writing cached JSON data back to a Google Sheet, ensuring alignment with existing header structure.

These utilities are essential for applications involving regular data synchronization
    between a backend system (cache or database) and Google Sheets, supporting tasks such as data migration,
    backup, and automated report generation.

Classes:
    GPT_Client: Handles interactions with the OpenAI GPT models for generating data based on attributes.
    LanchainWrapper: Encapsulates retrieval and handling of data using the LangChain API.

Exceptions:
    UnscorableCommentError: Custom exception for error handling specific to GPT client operations.

Dependencies:
    gspread: For interacting with Google Sheets.
    pandas and gspread_dataframe: For data manipulation and integration between DataFrames and Google Sheets.
    oauth2client: For Google API authentication.
    json: For parsing and handling JSON data structures.

Typical usage example:
    client = gspread.authorize(credentials)
    worksheet = client.open('My Spreadsheet').sheet1
    clear_worksheet_content(worksheet)
    write_cache_to_worksheet('path/to/cache.json', worksheet)
"""

from typing import Dict, List
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread_dataframe import get_as_dataframe
import pandas as pd
from university_info_generator.configs import config
from .save_load_utility import load_cache


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
def recreate_sheet(
    sheet_client: gspread.Client = get_sheet_client(),
    title: str = "output",
    spreadsheet_title: str = "working_extract_info_output",
):
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
) -> pd.DataFrame:
    """
    Retrieves attribute data from a specified Google Sheets worksheet and converts it into a dictionary.

    This function accesses a Google Sheet specified by the `spreadsheet_title` and `sheet_title`, reads the data,
    cleans up any rows that are entirely NaN (i.e., completely empty), and then converts the data into a dictionary
    where each attribute name becomes a key pointing to another dictionary of that attribute's details.

    Parameters:
        sheet_client (gspread.Client): A gspread Client object used to interact with Google Sheets.
            Default: obtained from `get_sheet_client()`.
        spreadsheet_title (str): The title of the spreadsheet from which data is to be read.
            Default: "working_extract_info_output".
        sheet_title (str): The title of the specific worksheet within the spreadsheet from which data is to be read.
            Default: "university_attribute_format".

    Returns:
        Dict[str, Dict[str, str]]: A dictionary where each key is an attribute name and each value is another
        dictionary containing details for that attribute. Details include fields such as format, prompt,
        reference URLs, examples, etc.

    Raises:
        gspread.exceptions.SpreadsheetNotFound: If the spreadsheet specified does not exist.
        gspread.exceptions.WorksheetNotFound: If the worksheet specified does not exist within the spreadsheet.

    Example:
        >>> # Assuming a gspread client is already set up
        client = gspread.authorize(credentials)
        attribute_dict = get_attribute_dict(client, "My Spreadsheet", "Attribute Definitions")
        print(attribute_dict['university_type'])
        # Outputs the dictionary of details for the 'university_type' attribute
    """
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
    """
    load result of get_attribute_df as Dict[str, Dict[str, str]]
    """
    data_frame = get_attribute_df(sheet_client, spreadsheet_title, sheet_title)
    data_frame = data_frame.dropna(how="all")  # Clean up the DataFrame
    data_frame.set_index("attribute_name", inplace=True)
    return data_frame.to_dict(orient="index")


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
    """
    Clears all data in a Google Sheets worksheet, starting from the second row, preserving only the header.

    This function is designed to clear content from a specified worksheet without removing the header row.
    It assesses the total number of rows and columns that contain data and clears everything from the second row
    downwards. This is particularly useful for resetting data in a worksheet while maintaining the structure
    defined by the header row.

    Parameters:
        worksheet (gspread.worksheet): The worksheet object from which all data except the headers will be cleared.

    Effects:
        Modifies the worksheet by setting the values of all cells from the second row onwards to empty strings.
        This operation retains the header row (the first row) and clears any data rows below it.

    Raises:
        gspread.exceptions.GSpreadException: An error occurred if the worksheet cannot be accessed or updated.

    Usage:
        Intended for scenarios where periodic data resets are required without altering the worksheet's column
        definitions provided in the header. This can be used in applications such as data entry forms, logs,
        or temporary data collection spreadsheets where data is regularly cleared after processing or archiving.

    Example:
        # Assuming 'client' is a gspread client and 'sheet' is an already opened spreadsheet
        worksheet = client.open('Data Entry Sheet').sheet1
        clear_worksheet_content(worksheet)
        print("Worksheet content has been cleared, headers remain intact.")
    """
    # Find the number of rows and columns to clear
    all_data = worksheet.get_all_values()
    num_rows = len(all_data)
    num_cols = len(all_data[0]) if num_rows > 0 else 0

    # Check if there's more than one row (data rows beyond the header)
    if num_rows > 1:
        # Build the range to clear: starts from row 2 to the last row
        cell_list = worksheet.range("A2:" + gspread.utils.rowcol_to_a1(num_rows, num_cols))
        for cell in cell_list:
            cell.value = ""
        worksheet.update_cells(cell_list)
        print(f"Cleared {num_rows - 1} rows and {num_cols} columns.")


def write_cache_to_worksheet(filepath: str, worksheet: gspread.worksheet):
    """
    Writes cache data from a JSON file to a Google Sheets worksheet, ensuring data consistency with existing columns.

    This function reads cache data from a specified JSON file, processes it into a pandas DataFrame, and appends
    each row of the DataFrame to a provided Google Sheets worksheet. It ensures that the DataFrame columns
    align with the headers in the worksheet, raising an error if there are missing columns. This function
    handles data cleaning by replacing NaN values with empty strings and ensures that data is appended in
    the correct column order as defined by the worksheet's header row.

    Parameters:
        filepath (str): The file path to the JSON cache file. This file should contain serialized JSON objects,
                        each representing a row of data to be written to the worksheet.
        worksheet (gspread.worksheet): The worksheet object to which the data will be appended. This worksheet
                                        should already have headers defined in its first row.

    Raises:
        FileNotFoundError: Raised if the JSON cache file specified does not exist or cannot be found.
        ValueError: Raised if the DataFrame constructed from the JSON file is missing columns that are present
                    in the worksheet headers, indicating a potential data consistency issue.
        Exception: Catches and logs other generic exceptions that could occur during the execution, such as issues
                    with reading the file, DataFrame manipulation, or appending data to Google Sheets.

    Usage:
        This function is intended for use in scenarios where periodic updates from a JSON-based cache to a
        Google Sheet are required, such as syncing processed data for reporting or further analysis.

    Example:
        # Assuming 'client' is a gspread client and 'sheet' is an already opened spreadsheet
        worksheet = client.open('Cache Data Sheet').sheet1
        write_cache_to_worksheet('path/to/cache.json', worksheet)
    """
    try:
        # Load the cached data into a pandas DataFrame
        cache_data = load_cache(filepath)

        # If the cached data is a dictionary of dictionaries, convert it to a list of dictionaries
        if isinstance(cache_data, dict):
            cache_data = list(cache_data.values())

        # Create a DataFrame from the list of dictionaries
        universities_df = pd.DataFrame(cache_data)

        # Cleanse the DataFrame by replacing NaN with empty strings
        universities_df.fillna("", inplace=True)

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
    except Exception as exc:
        print(f"An error occurred: {str(exc)}")


__all__ = [name for name in dir() if name[0] != "_"]
