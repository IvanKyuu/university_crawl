"""
university_info_generator/configs/config.py
"""

import os
from dotenv import load_dotenv

# Base project directory
# TODO: change this for your own path or name
PROJECT_HOME = os.getenv("PROJECT_HOME", "/home/ivan/Uforse/university_crawl")

# Configuration specific to the project
CONFIG_REPO_PATH = os.path.join(PROJECT_HOME, "university_info_generator/configs")
# TODO: change this for your own path or name
CREDENTIAL_JSON_PATH = os.path.join(CONFIG_REPO_PATH, "uforseAdminKey.json")
CACHE_REPO_PATH = os.path.join(PROJECT_HOME, "cache_repo")
UNIVERSITY_ATTRIBUTE_CACHE_FILE_PATH = os.path.join(CACHE_REPO_PATH, "university_attribute_format.jsonl")
ENV_PATH = ".env"
ENV_FILE_PATH = os.path.join(CONFIG_REPO_PATH, ENV_PATH)
CACHE_MAX_SIZE = 128
load_dotenv(ENV_FILE_PATH)
# OPENAI_API_KEY = os.getenv("IVAN_OPENAI_API_KEY")
# "sk-proj-uJWauYc0WHbWJifWhAZDT3BlbkFJlsM9la9PBe9ZJXhNimiU"
# "sess-L4EL6u1AXraNIdbsbgIBK8VAlgAQdYliWlQT1FmI"
# "sk-proj-INnFANHWe1zF0v5BCM9uT3BlbkFJqTnxws7K6n4h1tXBaDfh"
# "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"
# "sk-4PdAcG1gbX0ukSIk81C354D860E146Ff813e9083E030258b"
# "sk-proj-l2GjfoMpeSoGimPxRgO9T3BlbkFJeyi14fcj6BfYDzjXZ3Lp"
OPENAI_API_KEY = "sk-proj-l2GjfoMpeSoGimPxRgO9T3BlbkFJeyi14fcj6BfYDzjXZ3Lp"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
# 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
# TAVILY_API_KEY=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
# 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
# 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
# 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
# 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
# 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
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_KEY = "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"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_PERSONAL_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
DEFAULT_OPENAI_MODEL = "gpt-4-turbo-2024-04-09"
# DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo-0125"
DEFAULT_K_VALUE = 10

__all__ = [name for name in dir() if name[0] != "_" and name != "os"]
