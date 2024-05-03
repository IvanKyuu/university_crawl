"""
This module provides tools and classes for managing and generating comprehensive university information.

It includes classes that handle the retrieval, storage, and processing of detailed university data from various sources,
including direct API calls, web scraping, and interactions with machine learning models. The primary goal of this module
is to offer a centralized, efficient, and reusable way to manage university-related data across educational platforms,
analytics tools, or any other systems requiring detailed and reliable educational institution data.

Classes:
    UniversityInfoGenerator: Manages and generates comprehensive university profiles.

The module is designed to be modular and extensible, allowing for easy adaptation to new data sources or changes in
data retrieval methodologies. It also includes caching mechanisms to enhance performance and reduce the load on external
data sources.

Example Usage:
    # Create an instance of the university info generator
    info_generator = UniversityInfoGenerator()

    # Retrieve information for a specific university
    uw_info = info_generator.get_university_info('UW')
    print(uw_info)

This module is prepared for a larger system aimed at providing educational resources and insights through
    data-driven methods.
"""

from pprint import pprint
import json
import math
import threading
from functools import lru_cache
from typing import Any, Dict, List, Tuple, Union, Literal

import gspread
import numpy as np

from university_info_generator.configs import config
from university_info_generator.configs.enum_class import (
    AttributeColumnType,
    ALL_ATTRIBUTE_NAME,
    BasicInfoType,
    GPTMethodType,
    GeneralInfoType,
    HandlerType,
    SavedDictType,
)
from university_info_generator.fetcher._gpt_method import GPTClient
from university_info_generator.fetcher._langchain_method import LanchainWrapper
from university_info_generator.fetcher._tuition_crawl import TuitionCrawl
from university_info_generator.university import University
from university_info_generator.utility.save_load_utility import load_cache, store_cache


def _is_nan(value):
    """Check if the given value is NaN."""
    try:
        return math.isnan(float(value))
    except (ValueError, TypeError):
        return False


class UniversityInfoGenerator:
    """
    A class responsible for generating and managing comprehensive information about universities.

    This class encapsulates methods and attributes necessary to fetch, store, and manipulate detailed
    information about universities from various sources. It integrates functionalities such as
    retrieving data from external APIs, processing data using machine learning models, and caching results
    for efficient reuse.

    Attributes:
        university_basic_info_dict (Dict[str, Dict[str, str]]): A dictionary that stores basic information
            about universities, such as names and identifiers.
        university_info_dict (Dict[str, University]): A dictionary that stores instances of the University
            class, representing detailed information about each university.
        attribute_dict (Dict[str, Dict[str, Any]]): A dictionary that holds attributes and metadata for
            university attributes, such as data type and retrieval method.
        gpt_cache_dict (Dict[str, Tuple[Any, List[str]]]): A cache that stores results from GPT-based queries
            to prevent redundant API calls and speed up response times.


    Usage:
        The generator can be utilized to build and maintain a robust database of university information,
        supporting functionalities in educational platforms, analytics tools, or any application requiring
        detailed and reliable university data.

    Example:
        >>> info_generator = UniversityInfoGenerator()
        >>> university_info = info_generator.get_university_info('UW')
        >>> print(university_info)

    Note:
        The class is designed to be flexible and extendable, allowing for easy integration of new data sources
        and methods as they become relevant or available.
    """

    DEFAULT_CACHE_REPO_PATH = config.CACHE_REPO_PATH
    DEFAULT_ENCODING = "utf-8"

    token_not_know = ["not ranked", "not available", "not know", "N/A", "none available", "none"]

    def __init__(
        self,
        target_universities: Dict[str, str] = None,
        university_infos: Dict[str, University] = None,
        attributes: Dict[str, Dict[str, Union[str, HandlerType]]] = None,
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
        self.gpt_client = GPTClient()
        self.trouble_produced_dict = {}
        # self.get_retrieved_attr = LanchainWrapper.get_retrieved_attr_with_format

    def fine_tuning(self):
        """
        TODO: place holder for fine tuning
        """
        print("fine_tuning")
        raise NotImplementedError()

    def get_specific_dict_from_type(self, dict_type: SavedDictType) -> Dict[str, str]:
        """
        Retrieves a specific dictionary based on the given dictionary type from an enumerated list.

        Args:
            dict_type (SavedDictType): The specific type of dictionary to retrieve, which must be an enum instance
                                    from SavedDictType.

        Returns:
            Dict[str, str]: The dictionary corresponding to the provided dictionary type.
        """
        # Check if the provided dict_type is indeed an instance of SavedDictType
        if not isinstance(dict_type, SavedDictType):
            raise ValueError(f"Invalid type provided: {dict_type}. Expected a SavedDictType instance.")
        dict_attr_name = dict_type.name.lower() + "_dict"
        if not hasattr(self, dict_attr_name):
            raise AttributeError(f"No matching dictionary found for {dict_type.name}")
        return getattr(self, dict_attr_name)

    @classmethod
    def unpack_params(cls, params: Dict[str, Any], name: Union[str, AttributeColumnType]):
        # Access the appropriate dictionary based on the enum name
        return params.get(str(name), "")

    @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_basic_info(self, param: str, param_type: BasicInfoType) -> Dict[str, str]:
        """
        Retrieves basic information about a university based on a specified parameter and its type.

        This method accesses cached information if available; otherwise, it fetches the information using a GPT model
        configured within the system. The method utilizes a caching mechanism to avoid repetitive API calls for
        the same information, improving efficiency and response time.

        Args:
            param (str): The search parameter, typically the name of the university.
            param_type (BasicInfoType): The type of the parameter being provided, which determines the kind of basic
                                        information being retrieved (e.g., university name).

        Returns:
            Dict[str, str]: A dictionary containing key-value pairs of basic information about the university,
                            such as its name, website, and Wikipedia link.

        Raises:
            ValueError: If an invalid type is provided that is not recognized by `BasicInfoType`.
        """
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
    def get_info_by_attribute(
        self,
        university_name: str,
        attribute_name: str,
        handler: HandlerType = HandlerType.LANGCHAIN_TAVILY,
        params: dict[str, Any] = None,
    ) -> str:
        """
        Retrieves detailed information for a specific attribute of a university by applying a specified handling method.

        This method uses different handlers to fetch and process the required university attribute. Each handler
        corresponds to a specific retrieval technique, such as using web scraping, API calls, or LLM inquiries.

        Parameters:
            university_name (str): The name of the university from which to retrieve information.
            attribute_name (str): The specific attribute to be retrieved (e.g., 'tuition fees', 'ranking').
            handler (HandlerType, optional): The handler type to use for retrieving the attribute.
                Defaults to HandlerType.LANGCHAIN_TAVILY.
            params (dict[str, Any], optional): Additional parameters that might be required by the handler,
                such as formatting details or contextual hints.
                Note: checkout self.unpack_attribute_dict for more info.

        Returns:
            str: The retrieved information as a string, or an empty string if no information could be retrieved.

        Raises:
            ValueError: If the provided `handler` is not supported or if the attribute cannot be retrieved.

        Usage:
            This function is designed to flexibly use different methods for information retrieval, allowing
            for a customizable approach depending on the attribute and available resources. For example,
            tuition information might be directly scraped, while academic programs could be retrieved via an API.

        Examples:
            # Retrieving tuition information using a web scraping handler
            tuition_info = uni_gen.get_info_by_attribute("University of Example", "domestic_student_tuition", \
                HandlerType.TUITION_CRAWL)

            # Getting popular programs using a language model-based handler
            programs = uni_gen.get_info_by_attribute(university_name="UW", attribute_name="statistics", \
                handler=HandlerType.LANGCHAIN_TAVILY, params={"k_value": 5})
        """
        if attribute_name not in ALL_ATTRIBUTE_NAME:
            raise ValueError(f"Expect a member of configs.enum_class.ALL_ATTRIBUTE_NAME, but got {attribute_name}")
        if not isinstance(handler, HandlerType):
            raise ValueError(f"Expect a member of HandlerType, but got {handler}")
        university_json = self.initialize_university_json(university_name)
        university_json, reference = self.add_basic_university_info(university_json, university_name)
        university_name = temp if university_name != (temp := university_json["university_name"]) else university_name

        university_json = {}
        if handler == HandlerType.TUITION_CRAWL:
            # if attribute_name in ("domestic_student_tuition", "international_student_tuition")
            university_json = self.handle_tuition_info(university_json, university_name)
            if attribute_name in university_json and len(university_json[attribute_name]) > 0:
                return university_json
        if handler in HandlerType.LANGCHAIN_METHOD:
            university_json = self.process_attribute_with_langchain(
                university_json=university_json,
                university_name=university_name,
                attribute_name=attribute_name,
                reference=reference,
                handler=handler,
                params=params,
            )
            if attribute_name in university_json and len(university_json[attribute_name]) > 0:
                return university_json
        # last choice
        if attribute_name not in university_json or len(university_json[attribute_name]) <= 0:
            # if handler == HandlerType.GPT_GENERAL
            self.trouble_produced_dict.update({})
            university_json = self.process_attribute_with_gpt(
                university_json, university_name, attribute_name, reference, params
            )
        return university_json

    def initialize_university_json(self, university_name) -> Dict[str, Any]:
        """
        TODO: place holder for initializing university_json
        """
        return {"id_": "0", "university_name": university_name}

    def add_basic_university_info(
        self, university_json: Dict[str, str], university_name
    ) -> Tuple[Dict[str, str], List[str]]:
        """
        Adds basic university information to the provided university JSON dictionary based on a given university name.

        This method retrieves basic information about the university, such as its official website and Wikipedia page,
        using the `get_university_basic_info` method, and merges this information into the provided university JSON.
        It also sets a default university ID.

        Args:
            university_json (Dict[str, str]): The dictionary containing initial or existing data about the university.
            university_name (str): The name of the university for which basic information is being added.

        Returns:
            Tuple[Dict[str, str], List[str]]: A tuple where the first element is the updated university JSON dictionary
                                        and the second element is a List of string of the university's website and
                                        Wikipedia link serving as a reference.

        Procedure:
            - Retrieves basic information using `get_university_basic_info` with the university's name.
            - Updates the passed university JSON dictionary with this basic information.
            - TODO: Initializes or updates the 'id_' key to '0' as a placeholder for a future unique identifier.
            - Constructs a reference string from the university's website and Wikipedia URL, if available.
            - Returns the updated university JSON and the reference string.

        Usage:
            This method is used within a larger data assembly process where complete and updated university profiles
                are constructed for use in educational applications,
                providing users with quick access to basic university data.

        Example:
            >>> university_data = {}
            >>> updated_university_data, references = add_basic_university_info(university_data, 'Example University')
            >>> print(updated_university_data)
            {'university_name': 'Example University', "website": "https://www.example.edu", \
                'wikipedia': "https://en.wikipedia.org/wiki/Example_University", "id_": '0'}
            >>> print(references)
            'https://www.example.edu https://en.wikipedia.org/wiki/Example_University'
        """
        basic_json = self.get_university_basic_info(param=university_name, param_type=BasicInfoType.UNIVERSITY_NAME)
        university_json.update(basic_json)
        # TODO: add logic to produce id
        university_json.update({"id_": "0"})
        reference = [basic_json.get("website", ""), basic_json.get("wikipedia", "")]
        return university_json, reference

    def handle_tuition_info(self, university_json, university_name):
        """
        Handles the retrieval of tuition information for a specified university and updates the university JSON.

        This method uses the 'tuition_crawl' object to fetch tuition information, which includes both domestic and
        international student tuition fees. It updates the university JSON dictionary with this information.

        Args:
            university_json (Dict[str, str]): The dictionary containing data about the university.
            university_name (str): The name of the university for which tuition information is being retrieved.

        Returns:
            Dict[str, str]: The updated university JSON dictionary with the newly added tuition information.
        """
        basic_json = self.tuition_crawl.fetch_tuition(university_name)
        if isinstance(basic_json, dict):
            university_json["domestic_student_tuition"] = basic_json.get("domestic_student_tuition", "")
            university_json["international_student_tuition"] = basic_json.get("international_student_tuition", "")
        else:
            print(f"Unexpected result type from fetch_tuition: {basic_json} for university: {university_name}")
            self.trouble_produced_dict.update(
                {
                    (
                        university_name,
                        "tuition",
                        HandlerType.TUITION_CRAWL,
                    ): basic_json
                }
            )
        return university_json

    def unpack_attribute_dict(self, attribute_name: str, dict_to_unpack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and returns the specific attribute details from the attribute dictionary.

        This method retrieves formatting details, prompts, references, and examples associated with a given attribute
        name from the attribute dictionary.
        Args:
            attribute_name (str): The key corresponding to the attribute in the attribute dictionary where
                details are unpacked.
            dict_to_unpack (Dict[str, Any]): The dict to unpack, e.g. params, if no dict_to_unpack is given,
                self.attribute_dict[attribute_name] is used.
                Note: it can only unpack key, value pairs as attribute_dict[attribute_name].keys(); additional pairs
                    will be ignored.

        Returns:
            Dict[key: value]:
                Following the format of attribute_dict[attribute_name].
                - format_ (str): The specified output format for the attribute.
                - additional_reference (List[str]): Any reference links provided for further information
                    on the attribute.
                - attribute_prompt (str): Additional prompt information for retrieving or generating the attribute.
                - example (str): An example value for the attribute.
                - handler (config.HandlerType): The specified handler for retrieving the attribute.
                - k_value (int): int, k value for related docs loaded by retriever.
                - mapping (str): a more throughout explanation of the attribute, could be replacing the attribute's name
                    in the process of searching and retrieving.
        """
        if attribute_name not in ALL_ATTRIBUTE_NAME:
            raise ValueError(f"Expect a member of configs.enum_class.ALL_ATTRIBUTE_NAME, but got {attribute_name}")

        result: Dict[str, Any] = self.attribute_dict[attribute_name].copy()
        result.update(dict_to_unpack)
        for attribute in AttributeColumnType:
            if not result[attribute.value]:
                result[attribute.value] = attribute.get_default_value()

        k_value = result[AttributeColumnType.K_VALUE.value]
        try:
            k_value = int(k_value)
        except ValueError:
            print(f"Cannot convert '{k_value}' to an integer. Use default value instead")
            k_value = AttributeColumnType.K_VALUE.get_default_value()
        if k_value < 1:
            print(f"expect k_value >= 1, but got {k_value}. Use default value instead")
            k_value = AttributeColumnType.K_VALUE.get_default_value()
        reference = result[AttributeColumnType.ATTRIBUTE_REFERENCE.value]
        if isinstance(reference, str) and len(reference) > 0:
            reference = json.loads(reference)
        elif not isinstance(reference, list):
            reference = []
        result.update(
            {AttributeColumnType.K_VALUE.value: k_value, AttributeColumnType.ATTRIBUTE_REFERENCE.value: reference}
        )
        return result

    def process_attribute_with_gpt(
        self,
        university_json,
        university_name: str,
        attribute_name: str,
        reference: List[str],
        params: Dict[str, Any] = None,
    ):
        """
        Processes a university attribute using a GPT model, caches the result, and updates the university JSON.

        This method uses a GPT to retrieve detailed information about a specific attribute of a university.
        It first checks if the attribute data is already cached. If not, it retrieves the data from the GPT model,
        cleans it, and then updates the cache and the input university JSON dictionary with the new data.

        Args:
            university_json (Dict[str, str]): The dictionary containing data about the university.
            university_name (str): The name of the university for which the attribute is being processed.
            attribute_name (str): The name of the attribute to process.
            reference (List[str]): Additional reference text to be used in the GPT query for context.

        Returns:
            Dict[str, str]: The updated university JSON dictionary with the newly processed attribute data.

        Procedure:
            - Checks the GPT cache to see if the attribute data is already available.
            - If not in cache, unpacks the attribute details (format, prompt, etc.) and makes a call to the GPT client.
            - After retrieving the data, it is cleaned up to remove any irrelevant or mistaken parts.
            - The clean data is then cached and added to the university JSON dictionary.
            - Finally, the updated university JSON dictionary is returned.

        Usage:
            This method is particularly useful when integrating dynamic, AI-driven data retrieval into applications
            where up-to-date and detailed information about university attributes is crucial, such as in educational
            resource platforms or university comparison tools.
        """
        gpt_dict_key = str(((university_name, attribute_name), GPTMethodType.ATTRIBUTE_INFO))
        if gpt_dict_key in self.gpt_cache_dict:
            university_json[attribute_name] = self.gpt_cache_dict[gpt_dict_key][0]
            return university_json
        if params is not None:
            format_, additional_reference, extra_prompt, example, _, _, mapping = map(
                lambda x: __class__.unpack_params(
                    params=self.unpack_attribute_dict(
                        attribute_name=attribute_name, dict_to_unpack=params
                    ),
                    name=x,
                ),
                AttributeColumnType.__all__,
            )
        else:
            format_, additional_reference, extra_prompt, example, _, _, mapping = self.unpack_attribute_dict(
                attribute_name=attribute_name, dict_to_unpack=self.attribute_dict[attribute_name]
            )
        reference.extend(additional_reference)
        generated_attr, generated_reference = self.gpt_client.get_value_and_reference_from_gpt(
            university_name=university_name,
            target_attribute=mapping if (mapping != "") else attribute_name,
            format_=format_,
            reference=f"{reference}",
            data_example_pair=f"{university_name} {attribute_name} {example}",
            extra_prompt=extra_prompt,
        )
        # clean generated_attr if gpt find none, or it is making things up
        if isinstance(generated_attr, str):
            generated_attr = self.cleanup_rrm_generated_result(generated_attr)
        self.gpt_cache_dict.update({gpt_dict_key: (generated_attr, generated_reference)})
        university_json[attribute_name] = generated_attr
        return university_json

    def cleanup_rrm_generated_result(self, result: str):
        """
        Cleans up the result string from an external retrieval or LLMs by checking for unwanted tokens

        Returns:
        str: The cleaned result if no unwanted tokens are found, otherwise an empty string.
        """
        if np.asarray(list(map(lambda x: x in result.lower(), __class__.token_not_know))).any():
            return ""
        return result

    def process_attribute_with_langchain(
        self,
        university_json: Dict[str, str],
        university_name: str,
        attribute_name: str,
        reference: List[str],
        handler: HandlerType.LANGCHAIN_METHOD = HandlerType.LANGCHAIN_TAVILY,
        params: Dict[str, Any] = None,
    ):
        """
        Processes a specific university attribute using the LangChain Tavily handler to retrieve data.

        This method determines the appropriate handling strategy for the university attribute based on its nature.
        For ranking-related attributes, it calls the method to handle ranking information; for other attributes,
        it uses a general attribute retrieval method. The attribute's details are unpacked from the attribute
        dictionary, and the necessary information for the LangChain API call is prepared and executed.
        The result is then optionally cleaned and updated into the university's JSON representation.

        Args:
            university_json (Dict[str, str]): The dictionary representing the current state of the university.
            university_name (str): The name of the university being processed.
            attribute_name (str): The specific attribute of the university to process.
            reference (List[str]): Additional reference information that may aid in data retrieval.

        Returns:
            Dict[str, str]: The updated university JSON dictionary with the newly retrieved attribute value.

        Detailed Process:
            1. Unpack the attribute details from the attribute dictionary.
            2. Depending on whether the attribute is ranking-related, call the respective LangChain retrieval function.
            3. If the retrieval returns a string (indicating successful data fetch), optionally clean up the result
                using a designated cleanup method.
            4. Update the university JSON dictionary with the processed attribute value.

        This method integrates external API calls to LangChain Tavily and handles dynamic attribute processing, ensuring
        that each type of attribute is treated according to its specific retrieval needs.
        """
        # pprint(handler)
        if not isinstance(handler, HandlerType) or handler not in HandlerType.LANGCHAIN_METHOD:
            raise ValueError(
                f"Expect a handler of type: HandlerType.LANGCHAIN_METHOD \
                from {HandlerType.LANGCHAIN_METHOD.name}, but got {handler}"
            )
        if params:
            format_, additional_reference, extra_prompt, example, _, k_value, mapping = map(
                lambda x: __class__.unpack_params(
                    params=self.unpack_attribute_dict(
                        attribute_name=attribute_name, dict_to_unpack=params
                    ),
                    name=x,
                ),
                AttributeColumnType.__all__,
            )

        else:
            format_, additional_reference, extra_prompt, example, _, k_value, mapping = self.unpack_attribute_dict(
                attribute_name=attribute_name, dict_to_unpack=self.attribute_dict[attribute_name]
            )
        # pprint(f"{format_} {additional_reference} {example} {extra_prompt} {example} {k_value} {mapping}")
        # pprint(f"process_attribute_with_langchain {(additional_reference)}")
        if handler == HandlerType.LANGCHAIN_TAVILY and GeneralInfoType.is_ranking(attr_name=attribute_name):
            func = LanchainWrapper.get_retrieved_ranking_with_format_tavily
        else:
            reference.extend(additional_reference)
            if handler == HandlerType.LANGCHAIN_SERPER:
                func = LanchainWrapper.get_retrieved_attr_langchain_google_search
            else:
                func = LanchainWrapper.get_retrieved_attr_with_format_tavily
        # pprint(func)
        generated_attr = func(
            university_name=university_name,
            target_attribute=mapping if (mapping != "") else attribute_name,
            format_=format_,
            reference=f"{reference}",
            _data_example_pair=f"{example}",
            _extra_prompt=extra_prompt,
            k_value=k_value,
            _params=params
        )
        temp_generated_attr = generated_attr

        if isinstance(generated_attr, str):
            generated_attr = self.cleanup_rrm_generated_result(generated_attr)
        university_json[attribute_name] = generated_attr
        # pprint(f"process_attribute_with_langchain additional_reference:{additional_reference} {reference}")
        if temp_generated_attr != generated_attr:
            #     generated_attr = LanchainWrapper.get_retrieved_attr_langchain_google_search(
            #     university_name=university_name,
            #     target_attribute=mapping if (mapping != "") else attribute_name,
            #     format_=format_,
            #     reference=additional_reference if additional_reference else reference,
            #     # reference=["https://www.google.com/"],
            #     _data_example_pair=f"{example}",
            #     _extra_prompt=extra_prompt,
            #     k_value=k_value,
            #     params={"transformer": "RecursiveURL"}
            # )
            self.trouble_produced_dict.update({(university_name, attribute_name, handler): temp_generated_attr})
        return university_json

    # @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_info(self, university_name: str) -> University:
        """
        Gathers comprehensive information about a university by using various handlers and updates it
            into a University object.

        This method initializes a JSON structure for a university and populates it with data by calling different
            handlers based on attribute requirements and the handlers specified in the attribute dictionary.
            It manages how attributes like tuition fees and general information are fetched using specific
            services or by processing through LLMs.

        Args:
            university_name (str): The name of the university for which information is being gathered.

        Returns:
            University: An instance of the University class populated with all the relevant data about the university.

        Steps:
            1. Initialize the base JSON structure for university information.
            2. Add basic university information from predefined sources or caches.
            3. Iterate through each attribute specified in the system's attribute dictionary.
            4. Handle each attribute based on its designated handler (e.g., tuition information via crawlers,
                other attributes via LangChain or GPT models).
            5. For attributes without explicit data, use a GPT model to generate the required information.
            6. Convert the final JSON data into a University instance and update the
                central university information dictionary.

        This method ensures that the University instance it returns is filled with up-to-date and comprehensive
            information.
        """
        university_json = self.initialize_university_json(university_name)
        university_json, reference = self.add_basic_university_info(university_json, university_name)
        university_name = (
            temp
            if university_name != (temp := university_json[BasicInfoType.UNIVERSITY_NAME.value])
            else university_name
        )

        def process_attribute(attribute_name: str, university_json: Dict[str, str]):
            if (
                attribute_name in ("wikipedia", "website")
                and attribute_name in university_json
                and len(university_json[attribute_name]) > 0
            ):
                return
            if self.attribute_dict[attribute_name][AttributeColumnType.HANDLER.value] == HandlerType.TUITION_CRAWL:
                #  if attribute_name in ("domestic_student_tuition", "international_student_tuition")
                university_json = self.handle_tuition_info(university_json, university_name)
                if attribute_name in university_json and len(university_json[attribute_name]) > 0:
                    return
            if (
                handler := self.attribute_dict[attribute_name].get(
                    AttributeColumnType.HANDLER.value, HandlerType.LANGCHAIN_TAVILY
                )
            ) in HandlerType.LANGCHAIN_METHOD:
                university_json = self.process_attribute_with_langchain(
                    university_json=university_json,
                    university_name=university_name,
                    attribute_name=attribute_name,
                    reference=reference,
                    handler=handler,
                )
                if attribute_name in university_json and len(university_json[attribute_name]) > 0:
                    return
            if attribute_name not in university_json or len(university_json[attribute_name]) <= 0:
                # last choice
                # if self.attribute_dict[attribute_name]["handler"] == HandlerType.GPT_GENERAL
                self.trouble_produced_dict.update({(university_name, "tuition", HandlerType.TUITION_CRAWL): ""})
                # university_json = self.process_attribute_with_gpt(
                #     university_json, university_name, attribute_name, reference
                # )

        threads = []
        for attribute_name in self.attribute_dict:
            thread = threading.Thread(
                target=process_attribute,
                args=(
                    attribute_name,
                    university_json,
                ),
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

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
        """
        Loads data into a specific dictionary managed by the system from a provided dictionary.

        This method updates a specific dictionary designated by `dict_type` with data from `input_dict`.
        It also handles specific behavior for the ATTRIBUTE dictionary, such as setting default handler types
        if unspecified or improperly formatted.

        Args:
            dict_type (SavedDictType): An enum member specifying which type of dictionary to update.
            input_dict (Dict): The dictionary containing the data to be loaded into the specified type.

        Raises:
            ValueError: If `dict_type` is not a member of SavedDictType, or if `input_dict` is not a dictionary.
                        This ensures that the method is called with proper and expected parameters.

        Side effects:
            Modifies the internal state of dictionaries managed by the class by updating them with new data.
            Specifically for ATTRIBUTE type, it checks and modifies handler types based on their existence or value.
        """
        if dict_type not in SavedDictType:
            raise ValueError(f"Invalid type provided: {dict_type}. Expected a SavedDictType.")
        if not isinstance(input_dict, dict):
            raise ValueError("input_dict must be a dictionary.")
        self.get_specific_dict_from_type(dict_type).update(input_dict)
        if dict_type == SavedDictType.ATTRIBUTE:
            for attr in self.attribute_dict:
                for col in self.attribute_dict[attr]:
                    if col == AttributeColumnType.HANDLER.value:
                        if _is_nan(self.attribute_dict[attr][col]):
                            self.attribute_dict[attr][AttributeColumnType.HANDLER.value] = HandlerType.NOT_SPECIFIED
                        else:
                            self.attribute_dict[attr][AttributeColumnType.HANDLER.value] = HandlerType[
                                self.attribute_dict[attr][AttributeColumnType.HANDLER.value]
                            ]
                    elif _is_nan(self.attribute_dict[attr][col]):
                        self.attribute_dict[attr][col] = ""

    # @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_faculty(self, university_name: str) -> List[str]:
        """
        Retrieves the list of faculties offered by a specified university.

        This method fetches the university's details either as a dictionary or as an instance
        of the University class, and then extracts the 'popular_programs' attribute.
        The method returns the popular programs if they are available; otherwise, it returns None.

        Args:
            university_name (str): The name of the university for which to retrieve popular programs.

        Returns:
            List[str]: A list of popular program names offered by the university, or None if the
            information is not available or the university doesn't exist in the records.

        Raises:
            KeyError: If the 'faculty' key does not exist in the dictionary when the university
            data is a Dict type. This could indicate a discrepancy in the expected data structure.
        """
        university: Union[University, Dict[str, str]] = self.get_university_info(university_name)
        if isinstance(university, Dict):
            return dict(university)[GeneralInfoType.FACULTY.value]
        if isinstance(university, University):
            return university.get_attr(GeneralInfoType.FACULTY.value)
        return None

    # @lru_cache(maxsize=config.CACHE_MAX_SIZE)
    def get_university_popular_programs(self, university_name: str) -> List[str]:
        """
        Retrieves the list of popular programs offered by a specified university.

        This method fetches the university's details either as a dictionary or as an instance
        of the University class, and then extracts the 'popular_programs' attribute.
        The method returns the popular programs if they are available; otherwise, it returns None.

        Args:
            university_name (str): The name of the university for which to retrieve popular programs.

        Returns:
            List[str]: A list of popular program names offered by the university, or None if the
            information is not available or the university doesn't exist in the records.

        Raises:
            KeyError: If the 'popular_programs' key does not exist in the dictionary when the university
            data is a Dict type. This could indicate a discrepancy in the expected data structure.
        """
        university: Union[University, Dict[str, str]] = self.get_university_info(university_name)
        # print(university)
        if isinstance(university, Dict):
            return dict(university)[GeneralInfoType.POPULAR_PROGRAMS.value]
        if isinstance(university, University):
            return university.get_attr(GeneralInfoType.POPULAR_PROGRAMS.value)
        return None

    @DeprecationWarning
    def append_to(self, university_name: str, worksheet: gspread.worksheet) -> None:
        """
        This method is deprecated and will be removed in a future version.
        Use new_method() instead.

        Deprecation Warning:
            append_to() is deprecated; use
                university_info_generator.utility.google_sheet_utility.write_cache_to_worksheet
            instead.
        """
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
