"""
university_info_generator/configs/__init__.py
"""

from .enum_class import (
    SavedDictType,
    BasicInfoType,
    GPTMethodType,
    GeneralInfoType,
    AttributeColumnType,
    HandlerType,
    ALL_ATTRIBUTE_NAME,
)
from . import config

__all__ = [
    SavedDictType.__name__,
    BasicInfoType.__name__,
    GeneralInfoType.__name__,
    AttributeColumnType.__name__,
    GPTMethodType.__name__,
    "ALL_ATTRIBUTE_NAME",
    HandlerType.__name__,
    "config",
]
