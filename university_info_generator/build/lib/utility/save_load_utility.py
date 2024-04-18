from typing import Dict
import json


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
            json_string = json.dumps({key: value}) + "\n"  # Convert to JSON string with newline
            cache_file.write(json_string)



__all__ = [name for name in dir() if name[0] != "_"]
