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

from enum import Enum


class SavedDictType(Enum):
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


class BasicInfoType(Enum):
    """
    Enumeration for specifying different types of basic information attributes related to universities.
    Attributes:
    NOT_SPECIFIED (int): Default value indicating that no specific information type has been determined.

    UNIVERSITY_NAME (int): Represents the official name of the university.

    ABBREVIATION (int): Refers to the commonly used abbreviation or short form of the university's name.

    WEBSITE (int): Points to the official website URL of the university.
        This can be used for direct linking to the university's online resources.

    WIKIPEDIA (int): Indicates the URL to the Wikipedia page about the university.
        This is useful for providing users with a quick access to detailed and vetted background information.

    ID (int): Denotes a unique identifier for the university.
    """

    NOT_SPECIFIED = 0
    UNIVERSITY_NAME = 1
    ABBREVIATION = 2
    WEBSITE = 3
    WIKIPEDIA = 4
    ID = 5


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


class HandlerType(Enum):
    """# The `HandlerType` enum class is a placeholder for a brief summary or description of the purpose of the
        enum member. It is meant to provide a quick overview of what each enum member represents or is used for.
        In this case, it is used as a placeholder for describing the purpose of each enum member in the
            `HandlerType` enum class.

    Args:
        Enum
    """

    NOT_SPECIFIED = 0
    GPT_BASIC = 1
    LANGCHAIN_TAVILY = 2
    TUITION_CRAWL = 3
    GPT_GENERAL = 4


__all__ = [name for name in dir() if name[0] != "_"]
