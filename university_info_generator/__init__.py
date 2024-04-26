"""
This is the university_info_generator package. It provides tools and classes for generating and managing
university-related information, integrating Google Sheets utilities, and handling university-specific data structures.
"""

# from . import university_info_general_generator
from university_info_generator.university_info_general_generator import UniversityInfoGenerator
from university_info_generator import university, university_info_general_generator, utility, configs, fetcher
from university_info_generator.configs import config
from university_info_generator.university import University

from university_info_generator.configs.enum_class import BasicInfoType, GPTMethodType, SavedDictType, HandlerType

__version__ = "0.1.0"
__all__ = []

if hasattr(utility, "__all__"):
    __all__.extend(utility.__all__)

if hasattr(configs, "__all__"):
    __all__.extend(configs.__all__)

if hasattr(fetcher, "__all__"):
    __all__.extend(fetcher.__all__)

if hasattr(config, "__all__"):
    __all__.extend(config.__all__)

__enum_type__ = [BasicInfoType.__name__, GPTMethodType.__name__, SavedDictType.__name__, HandlerType.__name__]
__all__.extend(__enum_type__)

__all__.extend(university.__all__)
__all__.extend(university_info_general_generator.__all__)
# __all__.append(UniversityInfoGenerator.__name__)
