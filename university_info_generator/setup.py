from setuptools import setup, find_packages

setup(
    name="university_info_generator",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        # list your package dependencies here, e.g.,
        "pandas",
        "numpy",
        "gspread",
        "oauth2client",
        "openai",
        "python-dotenv",
        "gspread_dataframe",  # Adding gspread_dataframe
        "bs4",
        "tenacity",
    ],
    include_package_data=True,
    package_data={
        "university_info_generator": ["configs/*.json"],
    },
)
