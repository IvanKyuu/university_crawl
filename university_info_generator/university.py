"""
This module defines utilities and classes for handling university-related information, focusing on
    structured data management and conversion. It includes functionalities to handle attributes, manipulate university
    data, and facilitate the interaction between different formats and representations.

The `University` class is a core component, representing comprehensive details about universities.
    It encapsulates various attributes such as the university's name, location, type and statistics.
    The class provides methods for converting university data between English and Simplified Chinese representations,
    handling JSON data serialization, and managing attributes dynamically.

Functions:
    - str_to_list: Converts a string to a list of strings based on a given splitter.
    - University.json_to_university: Static method that deserializes JSON input into a `University` instance, supporting
        translations between English and Simplified Chinese.

Class:
    - University: Represents detailed information about a university, encapsulating attributes related to its
        identification, academic offerings, location, rankings, and etc.
        Provides methods for dictionary conversions and attribute access.

Usage:
    This module is intended for applications that require detailed and structured management of university data,
    particularly in environments where internationalization (i.e., support for both English and Chinese) is necessary.
    It facilitates easy transformations between different data representations (e.g., JSON, dictionaries) and provides
    utility functions to aid in data manipulation and extraction tasks.

Example:
    >>> university = University(
            id_=1,
            university_name="University of Waterloo",
            params={
                "abbreviation": "UW",
                "university_type": "Public",
                ...
            }
        )
    >>> print(university)
    University(ID=1, Name=University of Waterloo)

Dependencies:
    - json: For parsing and generating JSON formatted strings.
    - typing: For type annotations that enhance readability and maintainability of the code.

This module can be used in academic data management systems, university ranking websites, and other educational
platforms where detailed information about institutions is handled and displayed in multiple languages.
"""

import json
from typing import List, Dict, Union


def str_to_list(arg: Union[str, List[str]], splitter=None) -> List[str]:
    """
    Converts a single string into a list of substrings, or returns the list unchanged if the input is already a list.
    """
    if not isinstance(arg, str):
        return arg
    return list(arg.split(splitter)) if splitter else list(arg.split())


class University:
    """
    A class representing details about a university, encapsulating various attributes related to university information.

    Attributes:
        id (int): Unique identifier for the university, default is 0.
        university_name (str): The full name of the university.
        params (dict): A dictionary containing all other university-related information.
            which could contains:
            + abbreviation (str): The common abbreviation of the university's name.
            + university_type (str): The type of university (e.g., public, private).
            + graduation_year (float): Year of graduation.
            + location (List[str]): The geographical location(s) of the university.
            + graduation_rate (float): The graduation rate of the university.
            + domestic_student_tuition (float): Tuition fees for domestic students.
            + international_student_tuition (float): Tuition fees for international students.
            + description (str): A brief description of the university.
            + ranking (List[str]): Rankings of the university across various platforms or criteria.
            + website (str): Official website of the university.
            + important_calendar (str): Key dates and events in the university's academic calendar.
            + statistics (List[str]): List of important statistics about the university.
            + faculty (List[str]): List of faculties or departments within the university.
            + popular_programs (List[str]): List of popular academic programs offered by the university.
            + characteristics (List[str]): Distinctive features or characteristics of the university.
            + wikipedia (str): Wikipedia link for the university.
            + others (str): Additional information about the university.

    Methods:
        __init__: Initializes the University object with the provided values for its attributes.
        __repr__: Provides a simple string representation of the university.
        to_dict_ch: Returns a dictionary representation of the university's attributes with keys in Chinese.
        to_dict_en: Returns a dictionary representation of the university's attributes with keys in English.

    Example:
        >>> university = University(
                id_=1,
                university_name="University of Waterloo",
                params={
                    "abbreviation": "UW",
                    "university_type": "Public",
                    "graduation_year": 4,
                    "location": ["Waterloo, Ontario, Canada"],
                    "graduation_rate": 88.5,
                    "domestic_student_tuition": 8000,
                    "international_student_tuition": 32000,
                    "description": "Known for its cooperative education programs.",
                    "ranking": ["Top 100 Worldwide"],
                    "website": "https://www.uwaterloo.ca",
                    "important_calendar": "Fall Semester starts in September",
                    "statistics": ["Enrollment: 35000"],
                    "faculty": ["Engineering", "Mathematics", "Science"],
                    "popular_programs": ["Computer Science", "Mechanical Engineering"],
                    "characteristics": ["Innovative", "Entrepreneurial"],
                    "wikipedia": "https://en.wikipedia.org/wiki/University_of_Waterloo",
                    "others": ""
                }
            )
        >>> print(university)
        University(ID=1, Name=University of Waterloo)
    """

    ch_en_translation_map = {
        "id_": "id_",
        "学校名": "university_name",
        "缩写": "abbreviation",
        "学校类型": "university_type",
        "毕业时间": "graduation_year",
        "地理位置": "location",
        "毕业率": "graduation_rate",
        "本地学生学费": "domestic_student_tuition",
        "国际学生学费": "international_student_tuition",
        "简介": "description",
        "排名": "ranking",
        "QS新闻2024排名": "ranking_qs_news_2024",
        "美国新闻2023排名": "ranking_us_news_2023",
        "泰晤士2024排名": "ranking_times_rank_2024",
        "软科世界大学2023排名": "ranking_arwu_rank_2023",
        "学校官方网站": "website",
        "学校重要日历": "important_calendar",
        "统计数据": "statistics",
        "院校": "faculty",
        "专业": "programs",
        "热门专业": "popular_programs",
        "学校特色": "characteristics",
        "其他": "others",
        "维基百科页": "wikipedia",  # Assuming you might also have a wikipedia key as seen in previous examples
    }

    en_ch_translation_map = {
        "id_": "id_",
        "university_name": "学校名",
        "abbreviation": "缩写",
        "university_type": "学校类型",
        "graduation_year": "毕业时间",
        "location": "地理位置",
        "graduation_rate": "毕业率",
        "domestic_student_tuition": "本地学生学费",
        "international_student_tuition": "国际学生学费",
        "description": "简介",
        "ranking": "排名",
        "ranking_qs_news_2024": "QS新闻2024排名",
        "ranking_us_news_2023": "美国新闻2023排名",
        "ranking_times_rank_2024": "泰晤士2024排名",
        "ranking_arwu_rank_2023": "软科世界大学2023排名",
        "website": "学校官方网站",
        "important_calendar": "学校重要日历",
        "statistics": "统计数据",
        "faculty": "院校",
        "programs": "专业",
        "popular_programs": "热门专业",
        "characteristics": "学校特色",
        "others": "其他",
        "wikipedia": "维基百科页",
    }

    valid_keys = set(en_ch_translation_map.keys())

    # def __init__(self, **kwargs):
    #     for key, value in kwargs.items():
    #         setattr(self, key, value)

    def __repr__(self):
        return f"University(ID={self.id_}, Name={self.university_name})"

    def to_dict_ch(self):
        """Returns a dictionary of attributes with Chinese keys."""
        params = self.params if isinstance(self.params, dict) else {}
        translated_params = self.translate(params, self.en_ch_translation_map)
        return {"id_": self.id_, "学校名": self.university_name, **translated_params}

    def to_dict_en(self):
        """Returns a dictionary of attributes with English keys."""
        return {"id_": self.id_, "university_name": self.university_name, **self.params}

    def __init__(self, id_: int, university_name: str, params: Dict[str, str]):
        self.id_: int = id_
        self.university_name: str = university_name
        self.params: Dict[str, str] = params if params is not None else {}

    def get_attr(self, attr_name: str, default=None):
        """
        Retrieves the value of the specified attribute or a default value if the attribute does not exist.

        Parameters:
            attr_name (str): The name of the attribute to retrieve.
            default (any, optional): The default value to return if the attribute is not found. Default is None.

        Returns:
            any: The value of the attribute or the default value.
        """
        if attr_name not in __class__.valid_keys:
            raise ValueError(f"Expect a valid attribute name from University.valid_keys, but got '{attr_name}'")
        if attr_name == "id_":
            return self.id_
        if attr_name == "university_name":
            return self.university_name
        if attr_name in self.params:
            return self.params[attr_name]
        return default

    @staticmethod
    def translate(source_dict: Dict[str, str], translation_map: Dict[str, str]):
        """Translates dictionary keys from Chinese to English based on a provided translation map."""
        return {translation_map.get(key, key): value for key, value in source_dict.items()}

    @staticmethod
    def json_to_university(json_input, language="EN"):
        """Deserialize JSON input into a dictionary using a translation map for keys."""
        if language not in (language_option := ("EN", "CH")):
            raise ValueError(f"University only supports two language: {language_option}, but got {language}")
        data = json.loads(json_input)
        if language == "CH":
            data = University.translate(data, University.ch_en_translation_map)
        filtered_data = {
            key: data[key] for key in data if key in University.valid_keys and key not in ("id_", "university_name")
        }
        return University(data["id_"], data["university_name"], filtered_data)


__all__ = ["University"]


if __name__ == "__main__":
    from pprint import pprint

    university_data_ch = {
        "id_": 1,
        "国际学生学费": 53000,
        "地理位置": ["Cambridge, MA, USA"],
        "学校名": "Massachusetts Institute of Technology",
        "学校官方网站": "https://www.mit.edu",
        "学校特色": ["Innovative", "Research-oriented"],
        "学校类型": "Private",
        "学校重要日历": "Fall semester starts in September",
        "排名": ["Top 3 Worldwide"],
        "本地学生学费": 53000,
        "毕业时间": 2024,
        "毕业率": 94,
        "热门专业": ["Computer Science", "Electrical Engineering", "MBA"],
        "简介": "Known for its engineering and computer science programs.",
        "统计数据": ["Enrollment: 11,520"],
        "维基百科页": "https://en.wikipedia.org/wiki/MIT",
        "缩写": "MIT",
        "院校": ["Engineering", "Computer Science", "Business"],
    }

    # pprint(ubc.to_dict_en())
    json_data = json.dumps(university_data_ch, indent=4, ensure_ascii=False)
    uni = University.json_to_university(json_data, language="CH")
    pprint(uni.to_dict_ch())
    pprint(uni.get_attr("description"))
