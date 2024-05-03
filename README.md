# University Crawl

## Description

This module provides tools to fetch and process university-related data using various handlers such as web scraping, API calls, and language models. It is designed to retrieve specific attributes such as tuition fees, rankings, and program details from specified universities.

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/IvanKyuu/university_crawl.git
cd university_info_generator
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

Configuration
Before running the module, ensure you set up the necessary configuration:

Environment Variables: Set up the required environment variables for API keys and other credentials.Create a .env file in the ```uni_info_generator/university_info_generator/configs``` directory and add the following:
```plaintext
OPENAI_API_KEY=
LANGCHAIN_API_KEY=
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
TAVILY_API_KEY=
```

Google API Credentials: Place your google-service-account.json in the ```uni_info_generator/university_info_generator/configs``` directory or specify its path in the config.py file.
Usage
The module can be used to retrieve information about universities as follows:

Retrieving Information
Import the main class and utilize its methods to fetch data:

```python
from university_info_generator import UniversityInfoGenerator

# Initialize the generator
info_gen = UniversityInfoGenerator()

# Fetch statistics information using a tavily
uni_gen.get_info_by_attribute(university_name="UW", attribute_name="statistics", params={"k_value": 5})

# Get everything in a json/University format
programs = info_gen.get_university_info("name of the university")
```

Or run
```PROJECT_HOME/university_info_generator/fetch_logic/enhance_fetch_uni_info.ipynb```
after you change PROJECT_HOME in the ipynb.
