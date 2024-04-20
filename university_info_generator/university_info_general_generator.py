from functools import lru_cache
import json
from typing import Dict, List
import gspread
from openai import OpenAI
from pprint import pprint

from university_info_generator.university import University
from university_info_generator.fetcher._gpt_method import GPT_Client
from university_info_generator.fetcher._tuition_crawl import TuitionCrawl
from university_info_generator.configs.enum_class import BasicInfoType, SavedDictType, GPTMethodType
from university_info_generator.utility.save_load_utility import load_cache, store_cache
from university_info_generator.configs import config


class UniversityInfoGenerator:
    DEFAULT_CACHE_REPO_PATH = config.CACHE_REPO_PATH
    DEFAULT_ENCODING = "utf-8"

    def __init__(
        self,
        target_universities: Dict[str, str] = None,
        university_infos: Dict[str, University] = None,
        attributes: Dict[str, Dict[str, str]] = None,
        gpt_cache_list: Dict[tuple, str] = None,
    ):
        if target_universities is None:
            target_universities = {}
        if university_infos is None:
            university_infos = {}
        if attributes is None:
            attributes = load_cache(config.UNIVERSITY_ATTRIBUTE_CACHE_FILE_PATH)
        if gpt_cache_list is None:
            gpt_cache_list = {}

        self.university_basic_info_dict = target_universities
        self.university_info_dict = university_infos
        self.attribute_dict = attributes
        self.gpt_cache_dict = gpt_cache_list
        self.tuition_crawl = TuitionCrawl()
        self.gpt_client = GPT_Client()

    def train(self):
        pass

    def get_specific_dict_from_type(self, dict_type: SavedDictType) -> Dict[str, str]:
        # Check if the provided dict_type is indeed an instance of SavedDictType
        if not isinstance(dict_type, SavedDictType):
            raise ValueError(f"Invalid type provided: {dict_type}. Expected a SavedDictType instance.")

        # Access the appropriate dictionary based on the enum name
        dict_attr_name = dict_type.name.lower() + "_dict"
        if not hasattr(self, dict_attr_name):
            raise AttributeError(f"No matching dictionary found for {dict_type.name}")
        return getattr(self, dict_attr_name)

    @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_basic_info(self, param: str, param_type: BasicInfoType) -> Dict[str, str]:
        if param_type not in BasicInfoType:
            raise ValueError(f"Invalid type provided: {param_type}. Expected a BasicInfoType.")
        if param_type == BasicInfoType.UNIVERSITY_NAME and param in self.university_basic_info_dict:
            return self.university_basic_info_dict[param]
        gpt_dict_key = str((param, GPTMethodType.BASIC_INFO))
        if gpt_dict_key in self.gpt_cache_dict:
            result, _ = self.gpt_cache_dict[gpt_dict_key]
            return result
        json_str = self.gpt_client.get_university_name_from_gpt(param)
        target_data = json.loads(json_str)
        uni_name = target_data[BasicInfoType.UNIVERSITY_NAME.name.lower()]
        self.gpt_cache_dict[str((uni_name, GPTMethodType.BASIC_INFO))] = (target_data, [])
        if param != uni_name:
            self.gpt_cache_dict[str((param, GPTMethodType.BASIC_INFO))] = (target_data, [])
        self.university_basic_info_dict[uni_name] = target_data
        return target_data

    # @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_info_by_attribute(self, university_name: str, attribute_name: str) -> str:
        if len(self.attribute_dict) <= 0:
            raise Exception("Please load the attribute dictionary first.")
        if (
            gpt_dict_key := str(((university_name, attribute_name), GPTMethodType.ATTRIBUTE_INFO))
        ) in self.gpt_cache_dict:
            return self.gpt_cache_dict[gpt_dict_key][0]
        if university_name in self.university_info_dict:
            university: University = self.university_info_dict[university_name]
            return university.get_attr(attribute_name)
        result_university = self.get_university_info(university_name)
        return result_university.get_attr(attribute_name)

    # @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_info(self, university_name: str) -> University:
        if university_name in self.university_info_dict:
            return self.university_info_dict[university_name]
        reference = ""
        # TODO: add logic to produce id
        university_json = {"id_": "0", "university_name": university_name}
        basic_json = self.get_university_basic_info(param=university_name, param_type=BasicInfoType.UNIVERSITY_NAME)
        university_json.update(basic_json)
        reference += basic_json.get("website", "") + " " + basic_json.get("wikipedia", "")
        for attribute_name in self.attribute_dict:
            if (
                gpt_dict_key := str(((university_name, attribute_name), GPTMethodType.ATTRIBUTE_INFO))
            ) in self.gpt_cache_dict:
                university_json[attribute_name] = self.gpt_cache_dict[gpt_dict_key][0]
                continue
            if attribute_name in ("wikipedia", "website"):
                continue
            # separate the tuition logic to use crawl directly
            if attribute_name in ("domestic_student_tuition", "international_student_tuition"):
                basic_json = self.tuition_crawl.fetch_tuition(university_name)
                if isinstance(basic_json, dict):
                    university_json["domestic_student_tuition"] = basic_json.get("domestic_student_tuition", "N/A")
                    university_json["international_student_tuition"] = basic_json.get(
                        "international_student_tuition", "N/A"
                    )
                    continue
                # Log error or set default values
                print(
                    f"Unexpected result type from fetch_tuition: {basic_json} for university: {university_name}\nUse GPT instead"
                )
                # university_json["domestic_student_tuition"] = "N/A"
                # university_json["international_student_tuition"] = "N/A"
            format_, additional_reference, example, extra_prompt = self.attribute_dict[attribute_name]
            generated_attr, generated_reference = self.gpt_client.get_value_and_reference_from_gpt(
                university_name=university_name,
                target_attribute=attribute_name,
                format_=format_,
                reference=f"{reference} {additional_reference}",
                data_example_pair=f"{university_name} {attribute_name} {example}",
                extra_prompt=extra_prompt,
            )
            # TODO: exclude the case when gpt cannot find the subject
            if "ranking" in attribute_name:
                pprint(attribute_name)
            if "not ranked" in generated_attr.lower():
                generated_attr = ""
            self.gpt_cache_dict.update({gpt_dict_key: (generated_attr, generated_reference)})
            university_json[attribute_name] = generated_attr
        # print(university_json)
        generated_university: University = University.json_to_university(json.dumps(university_json), language="EN")
        self.university_info_dict.update({university_name: generated_university})
        return generated_university

    def save_to_file(self, dict_type: SavedDictType, file_path: str):
        """
        Saves the dictionary specified by dict_type to a JSON file at file_path.

        Parameters:
            dict_type (SavedDictType): The type of dictionary to save.
            file_path (str): The path to the file where the dictionary should be saved.

        Raises:
            ValueError: If the dict_type is not recognized or if the dictionary is empty.
        """
        target_dict = self.get_specific_dict_from_type(dict_type=dict_type)
        try:
            store_cache(file_path, target_dict)
        except IOError as exc:
            raise IOError(f"An error occurred while writing to the file: {file_path}") from exc

    def load_from_file(self, dict_type: SavedDictType, file_path: str):
        """
        Loads data from a JSON file and updates the corresponding dictionary
        in the class based on the specified type.

        Parameters:
            dict_type (SavedDictType): The type of dictionary to update.
            file_path (str): The path to the JSON file containing the data.

        Raises:
            ValueError: If the file content is not a valid JSON or dict_type is invalid.
        """
        if dict_type not in SavedDictType:
            raise ValueError(f"Invalid type provided: {dict_type}. Expected a SavedDictType.")
        try:
            data = load_cache(file_path)
            if not isinstance(data, dict):
                raise ValueError("The file content must be a JSON object.")
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"The file at {file_path} was not found.") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("Failed to decode JSON. Check file content for errors.") from exc

        # Using the existing method to load data into the class
        self.load_from_dict(dict_type, data)

    def load_from_dict(self, dict_type: SavedDictType, input_dict: Dict):
        if dict_type not in SavedDictType:
            raise ValueError(f"Invalid type provided: {dict_type}. Expected a SavedDictType.")
        if not isinstance(input_dict, dict):
            raise ValueError("input_dict must be a dictionary.")
        self.get_specific_dict_from_type(dict_type).update(input_dict)

    # @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_faculty(self, university_name: str) -> List[str]:
        university = self.get_university_info(university_name)
        if isinstance(university, Dict):
            return university["faculty"]
        if isinstance(university, University):
            return university.get_attr("faculty")
        return None

    # @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_popular_programs(self, university_name: str) -> List[str]:
        university = self.get_university_info(university_name)
        # print(university)
        if isinstance(university, Dict):
            return university["popular_programs"]
        if isinstance(university, University):
            return university.get_attr("popular_programs")
        return None

    def append_to(self, university_name: str, worksheet: gspread.worksheet) -> None:
        # Get data in a column format
        data = self.get_university_info(university_name)
        # Convert column data to row data
        row_data = [list(data.to_dict_en())]

        # Get the number of existing rows to determine where to start appending
        existing_rows = len(worksheet.get_all_values())
        # Append each "row" from row_data to the end of the worksheet
        for i, values in enumerate(zip(*row_data), start=existing_rows + 1):
            cell_range = worksheet.range(i, 1, i, len(values))  # Adjust range for the correct number of columns
            for cell, value in zip(cell_range, values):
                cell.value = value
            worksheet.update_cells(cell_range)

        print(f"Data for {university_name} appended to columns successfully.")


__all__ = ["UniversityInfoGenerator"]
