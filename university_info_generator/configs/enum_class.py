"""
This module defines several enumeration classes used throughout the university information system to standardize the
categorization and handling of different types of data and interactions.

The enumerations help ensure that data handling, GPT model interactions, and various processing tasks are conducted
consistently and according to predefined categories. This approach simplifies development, enhances maintainability,
and improves the system's overall robustness by providing a clear and structured way to refer to specific sets of
behaviors and data types.

Enumerations defined in this module include:

- `SavedDictType`: Classifies different categories of saved dictionaries, aiding in the structured storage and
    retrieval of data within the system.
- `BasicInfoType`: Specifies types of basic informational attributes about universities to ensure uniformity in data
    representation.
- `GPTMethodType`: Categorizes methods used in GPT model interactions, aligning model usage with the complexity and
    detail required by specific tasks.
- `HandlerType`: Defines types of handlers used for processing different operations, particularly in scenarios where
    specialized handling or routing is necessary.

These enums are integral to various system components, from data handling functions to user interface operations,
and are extensively used to maintain clarity and consistency across the system.
"""

from enum import Enum, auto, Flag
from typing import Any


class UniversitySavedDictType(Enum):
    """
    Enumeration for specifying different types of saved dictionaries used within the system.

    Attributes:
        UNIVERSITY_BASIC_INFO (int): Enum member representing the basic information about universities.
            This dictionary stores general data about universities, such as names, abbreviation, website and wiki.

        UNIVERSITY_INFO (int): Enum member for detailed university information.
            This includes comprehensive attributes beyond basic info
                including location, faculty, and specific important_calendar.

        ATTRIBUTE (int): Enum member representing specific name, format, reference, prompt, example and	handler.


        GPT_CACHE (int): Enum member used for caching results from GPT-based operations.
            This cache store processed calls from GPT models that are frequently accessed
                or computationally expensive to regenerate.

    Usage:
        This enum is used to key dictionaries that organize different categories of data in the system,
        allowing for structured access and manipulation of these data sets.
    """

    UNIVERSITY_BASIC_INFO = 1
    UNIVERSITY_INFO = 2
    ATTRIBUTE = 3
    GPT_CACHE = 4
    TROUBLE_PRODUCED = 5


class UniversityBasicInfoType(Enum):
    """
    Enumeration for specifying different types of basic information attributes related to universities.
    Attributes:
    NOT_SPECIFIED (int): Default value indicating that no specific information type has been determined.

    UNIVERSITY_NAME (str): Represents the official name of the university.

    ABBREVIATION (str): Refers to the commonly used abbreviation or short form of the university's name.

    WEBSITE (str): Points to the official website URL of the university.
        This can be used for direct linking to the university's online resources.

    WIKIPEDIA (str): Indicates the URL to the Wikipedia page about the university.
        This is useful for providing users with a quick access to detailed and vetted background information.

    ID (str): Denotes a unique identifier for the university.
    """

    NOT_SPECIFIED = 0
    UNIVERSITY_NAME = "university_name"
    ABBREVIATION = "abbreviation"
    WEBSITE = "website"
    WIKIPEDIA = "wikipedia"
    ID = "id_"
    __all__ = ["university_name", "abbreviation", "website", "wikipedia", "id_"]


# TODO: refactor everything!
class UniversityGeneralInfoType(Enum):
    """
    Enumeration for specifying different types of general information attributes related to universities.
    These members represent the various data points that can be associated with universities,
    such as tuition fees, location, academic programs, etc.

    Attributes:
        GRADUATION_YEAR (str): Represents the typical graduation year for a program at the university.
        LOCATION (str): Geographical location(s) of the university.
        GRADUATION_RATE (str): The percentage of students who graduate from the university.
        DOMESTIC_STUDENT_TUITION (str): Annual tuition fees for domestic students.
        INTERNATIONAL_STUDENT_TUITION (str): Annual tuition fees for international students.
        DESCRIPTION (str): A brief description of the university.
        RANKING_QS_NEWS_2024 (str): QS World University Rankings for the year 2024.
        RANKING_US_NEWS_2023 (str): US News & World Report University Rankings for the year 2023.
        RANKING_TIMES_RANK_2024 (str): Times Higher Education World University Rankings for the year 2024.
        RANKING_ARWU_RANK_2023 (str): Academic Ranking of World Universities for the year 2023.
        WEBSITE (str): Official website of the university.
        IMPORTANT_CALENDAR (str): Key dates and events in the university's academic calendar.
        STATISTICS (str): Important statistics about the university, such as enrollment numbers.
        FACULTY (str): List of faculties or departments within the university.
        POPULAR_PROGRAMS (str): List of popular academic programs offered by the university.
        PROGRAMS (str): General listing of academic programs available at the university.
        CHARACTERISTICS (str): Distinctive features or characteristics of the university.
        WIKIPEDIA (str): Wikipedia link for more information about the university.
        OTHERS (str): Any other additional information about the university.

    Usage:
        This enum is used to key dictionaries that organize different categories of data in systems
            dealing with university information, allowing for structured access and manipulation of these data sets.
    """

    UNIVERSITY_TYPE = "university_type"
    GRADUATION_YEAR = "graduation_year"
    LOCATION = "location"
    GRADUATION_RATE = "graduation_rate"
    DOMESTIC_STUDENT_TUITION = "domestic_student_tuition"
    INTERNATIONAL_STUDENT_TUITION = "international_student_tuition"
    DESCRIPTION = "description"
    RANKING_QS_NEWS_2024 = "ranking_qs_news_2024"
    RANKING_US_NEWS_2023 = "ranking_us_news_2023"
    RANKING_TIMES_RANK_2024 = "ranking_times_rank_2024"
    RANKING_ARWU_RANK_2023 = "ranking_arwu_rank_2023"
    WEBSITE = "website"
    IMPORTANT_CALENDAR = "important_calendar"
    STATISTICS = "statistics"
    FACULTY = "faculty"
    POPULAR_PROGRAMS = "popular_programs"
    PROGRAMS = "programs"
    CHARACTERISTICS = "characteristics"
    WIKIPEDIA = "wikipedia"
    OTHERS = "others"

    @classmethod
    def is_ranking(cls, attr_name: str):
        return "ranking" in attr_name

    # __all__ = [class]

    # TODO: add default here
    def get_default_value(self):
        """
        Wrapper to get the default value
        """
        __default_value_dict__ = {
            __class__.GRADUATION_YEAR: 4,
        }
        return __default_value_dict__[self.name]


class UniversityAttributeColumnType(Enum):
    """
    Enumeration defining the columns of attribute data in a system that manages university information.
    These members represent the different types of data columns that can be used to describe attributes
    related to university information management.

    Attributes:
        ATTRIBUTE_FORMAT (str): The expected format of the attribute value.
        ATTRIBUTE_REFERENCE (str): References or sources providing more information about the attribute.
        ATTRIBUTE_PROMPT (str): A prompt or description to guide data entry or explain the attribute's use.
        EXAMPLE (str): Example data to illustrate how the attribute values should appear.
        HANDLER (str): Specifies the method or handler responsible for processing or fetching this attribute.
        K_VALUE (str): A parameter used in algorithms or queries, usually defining the number or scope of items
            to fetch or consider.
        MAPPING (str): Defines how this attribute maps to other data structures or external databases.

    Usage:
        This enum is used within systems that require structured definitions of data attributes, such as databases,
        data ingestion pipelines, or data management interfaces. It helps ensure that all parts of the system
        consistently refer to these attributes by the same standards.
    """

    ATTRIBUTE_FORMAT = "attribute_format"
    ATTRIBUTE_REFERENCE = "attribute_reference"
    ATTRIBUTE_PROMPT = "attribute_prompt"
    EXAMPLE = "example"
    HANDLER = "handler"
    K_VALUE = "k_value"
    MAPPING = "mapping"

    def __str__(self) -> str:
        return self.value

    # TODO: add default here
    def get_default_value(self) -> Any:
        """
        Wrapper to get the default value
        """
        __default_value_dict__ = {
            "k_value": 10,
            "handler": "LANGCHAIN_TAVILY",
        }
        return __default_value_dict__.get(self.value, "")

    __all__ = [
        "attribute_format",
        "attribute_reference",
        "attribute_prompt",
        "example",
        "handler",
        "k_value",
        "mapping",
    ]


class GPTMethodType(Enum):
    """
    Enumeration defining the types of methods used when interacting with GPT models within the system.

    Attributes:
        BASIC_INFO (int): Enum value representing operations that retrieve basic information.
            This method type is used for general inquiries for BasicInfoType.

        ATTRIBUTE_INFO (int): Represents operations that retrieve detailed attribute information.
            This method is used when specific, detailed information is needed about certain attributes of an entity.
            Suitable for deep dives or when precise and extensive details are necessary to fulfill the query or task.

    Usage:
        This enum helps in categorizing the type of GPT model operations, facilitating the appropriate routing of
            requests and handling of responses based on the complexity and detail level of the information required.
    """

    BASIC_INFO = 1
    ATTRIBUTE_INFO = 2


class HandlerType(Flag):
    """# The `HandlerType` enum class is a placeholder for a brief summary or description of the purpose of the
        enum member. It is meant to provide a quick overview of what each enum member represents or is used for.
        In this case, it is used as a placeholder for describing the purpose of each enum member in the
            `HandlerType` enum class.

    Args:
        Enum
    """

    NOT_SPECIFIED = auto()
    GPT_BASIC = auto()
    GPT_GENERAL = auto()
    TUITION_CRAWL = auto()
    LANGCHAIN_TAVILY = auto()
    LANGCHAIN_SERPER = auto()
    RANKING_FETCHER = auto()
    PROGRAM_FETCHER = auto()
    LANGCHAIN_METHOD = LANGCHAIN_TAVILY | LANGCHAIN_SERPER


ALL_ATTRIBUTE_NAME = [member.value for member in UniversityBasicInfoType] + [
    member.value for member in UniversityGeneralInfoType
]

__all__ = [name for name in dir() if name[0] != "_"]
