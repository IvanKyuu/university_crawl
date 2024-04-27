"""
This module provides functionalities for managing cache operations for the university information system.
It includes methods to load data from and store data to a JSON-formatted cache file. These operations are
crucial for reducing redundant API calls or database queries by storing frequently accessed or computationally
intensive data in a local cache.

The module's functions support handling custom data types, such as instances of the `University` class, by
converting them to a dictionary format suitable for JSON serialization. This facilitates the easy retrieval
and updating of cached university data in a structured and efficient manner.

Functions:
    load_cache(cache_path: str) -> Dict[str, Dict[str, str]]:
        Loads cache data from a JSON file located at the specified path. This function reads the file line by line,
        attempting to deserialize each line as a JSON object and collect them into a dictionary. It handles
        potential issues such as file not found errors or JSON decoding errors by printing relevant messages.

    store_cache(cache_path: str, cache: Dict[str, str]):
        Stores a dictionary of data into a JSON file at the given path. Each key-value pair in the dictionary
        is serialized into a JSON string and written to the file on a new line. Special handling is included
        for keys that are tuples and values that are instances of the `University` class, ensuring they are
        properly serialized.

This module is typically used within backend services where caching of processed or retrieved data is required
to enhance performance and responsiveness of the university information system.

Example Usage:
    # Load existing cache data
    cache_data = load_cache('path/to/cache.json')

    # Update cache with new data
    cache_data['new_key'] = {'info': 'value'}
    store_cache('path/to/cache.json', cache_data)

Note:
    The cache management implemented here is simple and aimed at small to medium-sized datasets. For handling
    larger datasets or more complex caching needs, consider integrating a dedicated caching service or database.
"""

from typing import Dict
import json
from university_info_generator.university import University


def load_cache(cache_path: str) -> Dict[str, Dict[str, str]]:
    """
    Loads and returns the cache from a JSON file.

    Args:
        cache_path (str): The file path to the JSON cache file.

    Returns:
        dict: The loaded cache data.
    """
    cache_data = {}
    try:
        with open(cache_path, "r", encoding="utf-8") as cache_file:
            for line_number, line in enumerate(cache_file, start=1):
                try:
                    line_data = json.loads(line.strip())
                    cache_data.update(line_data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON on line {line_number}: {line.strip()}")
    except FileNotFoundError:
        print(f"No such file: {cache_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return cache_data


def store_cache(cache_path, cache: Dict[str, str]):
    """
    Stores the provided cache dictionary into a JSON file at the specified path.

    Args:
        cache_path (str): The file path where the cache will be stored.
        cache (dict): The cache data to store.

    Returns:
        None
    """
    with open(cache_path, "w", encoding="utf-8") as cache_file:
        for key, value in cache.items():
            if isinstance(key, tuple):
                key = str(key)
            if isinstance(value, University):
                value = value.to_dict_en()
            json_string = json.dumps({key: value}) + "\n"  # Convert to JSON string with newline
            cache_file.write(json_string)


__all__ = [name for name in dir() if name[0] != "_"]
