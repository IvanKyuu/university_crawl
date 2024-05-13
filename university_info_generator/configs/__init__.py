"""
university_info_generator/configs/__init__.py
"""

from .enum_class import (
    UniversitySavedDictType,
    UniversityBasicInfoType,
    GPTMethodType,
    UniversityGeneralInfoType,
    UniversityAttributeColumnType,
    HandlerType,
    ALL_ATTRIBUTE_NAME,
)
from . import config

__all__ = [
    UniversitySavedDictType.__name__,
    UniversityBasicInfoType.__name__,
    UniversityGeneralInfoType.__name__,
    UniversityAttributeColumnType.__name__,
    GPTMethodType.__name__,
    "ALL_ATTRIBUTE_NAME",
    HandlerType.__name__,
    "config",
]
