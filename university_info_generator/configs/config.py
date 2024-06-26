"""
university_info_generator/config.py
"""

import os
from dotenv import load_dotenv

# Base project directory
PROJECT_HOME = os.getenv("PROJECT_HOME", "/home/ivan/Uforse/uni_info_generator")

# Configuration specific to the project
CONFIG_REPO_PATH = os.path.join(PROJECT_HOME, "university_info_generator/configs")
CREDENTIAL_JSON_PATH = os.path.join(CONFIG_REPO_PATH, "uforseAdminKey.json")
CACHE_REPO_PATH = os.path.join(PROJECT_HOME, "cache_repo")
UNIVERSITY_ATTRIBUTE_CACHE_FILE_PATH = os.path.join(CACHE_REPO_PATH, "university_attribute_format.jsonl")
ENV_PATH = ".env"
ENV_FILE_PATH = os.path.join(CONFIG_REPO_PATH, ENV_PATH)
CACHE_MAX_SIZE = 128
load_dotenv(ENV_FILE_PATH)
OPENAI_API_KEY = os.getenv("UFORSE_OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
OPENAI_MODEL = "gpt-4-turbo-2024-04-09"

__all__ = [name for name in dir() if name[0] != "_" and name != "os"]
