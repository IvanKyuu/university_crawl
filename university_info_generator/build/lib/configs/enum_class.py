from enum import Enum


class SavedDictType(Enum):
    UNIVERSITY_BASIC_INFO = 1
    UNIVERSITY_INFO = 2
    ATTRIBUTE_LIST = 3
    GPT_CACHE = 4


class BasicInfoType(Enum):
    NOT_SPECIFIED = 0
    UNIVERSITY_NAME = 1
    ABBREVIATION = 2
    WEBSITE = 3
    WIKIPEDIA = 4


class GPTMethodType(Enum):
    BASIC_INFO = 1
    ATTRIBUTE_INFO = 2


__all__ = [name for name in dir() if name[0] != "_"]
