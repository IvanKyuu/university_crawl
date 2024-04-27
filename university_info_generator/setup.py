"""
university_info_generator/setup.py

"""

from setuptools import setup, find_packages

setup(
    name="university_info_generator",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        # list the package dependencies here
        "pandas",
        "numpy",
        "gspread",
        "oauth2client",
        "openai",
        "python-dotenv",
        "gspread_dataframe",
        "bs4",
        "tenacity",
        # env for langchain
        "langchain",
        "langchain-openai",
        "apify-client",
    ],
    include_package_data=True,
    package_data={
        "university_info_generator": ["configs/*.json"],
    },
)
