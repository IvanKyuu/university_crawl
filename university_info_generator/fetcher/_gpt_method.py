"""
This module provides functionality to interact with OpenAI's API for retrieving detailed information about
Canadian universities and managing spreadsheet data for a given set of university records. It leverages the
OpenAI GPT models to fill in missing university data based on user input and predefined prompts, and handles
data retrieval with robust error management using retries and exponential backoff strategies.

The module is structured to support tasks such as fetching JSON data from the OpenAI API based on the name
or URL of a university, and updating spreadsheets with missing university data. It includes custom exception
handling, caching mechanisms, and spreadsheet operations using the gspread library.

Key Functions:
- get_university_name_from_gpt: Fetches information about a university using the OpenAI API and
    returns it in JSON format.
- get_value_and_reference_from_gpt: Retrieves specific attribute values and references for a given university
    using the OpenAI API.
- fill_missing_entry: Updates missing entries in a worksheet based on the data fetched using OpenAI.
- fill_target_university: A wrapper function to manage worksheet updates for university records.

Custom Exceptions:
- UnscorableCommentError: Custom exception to handle specific error cases in OpenAI responses.

Dependencies:
- openai: Python client library for accessing OpenAI's API.
- gspread: Python library for interacting with Google Sheets.
- dotenv: Python library for managing environment variables.
- tenacity: Python library for retrying failing operations with customizable strategies.

Usage:
The module should be utilized in environments where OpenAI's API access is configured, and Google Sheets API
credentials are set up for gspread operations. Ensure all required environment variables are available through
a .env file or environment settings.

Example Usage:
To use the functions for filling missing university data in a Google Sheet, call the fill_target_university
function after setting up the appropriate API keys and sheet credentials.

"""

import json
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from openai import APIConnectionError, APIError, RateLimitError
from tenacity import retry, wait_random_exponential, retry_if_exception_type, stop_after_attempt
from university_info_generator.configs import config


class UnscorableCommentError(Exception):
    """
    Exception raised for comments that cannot be scored.

    This exception is used to indicate a scenario where a comment does not meet the criteria for scoring,
    due to factors such as format, content, or context inadequacies.

    Usage:
        Able GPT to retry upon unscorable situations
    """



class GPTClient:
    """
    A client class for interfacing with the OpenAI GPT models.

    This class handles the initialization and management of connections to OpenAI's API using credentials
    stored in environment variables. It provides methods to perform various operations using GPT models,
    such as retrieving university names or other specific information based on input queries.

    Attributes:
        api_key (str): The API key required to authenticate requests to the OpenAI API.
        gpt_basic_client (OpenAI): A basic GPT client for general operations.
        gpt_client (OpenAI): An enhanced GPT client configured for more specific or complex operations.

    Methods:
        get_university_name_from_gpt(name: str) -> str:
            Retrieves the name of a university from the GPT model based on a given input name.

    Raises:
        KeyError: If the OpenAI API key is not found in the configuration, indicating that the client
            cannot be properly initialized without necessary credentials.

    Usage:
        This class is typically used where GPT-based textual analysis or generation is required,
            especially in contexts involving educational data processing or any application requiring
            access to up-to-date, AI-generated content.
    """

    def __init__(self):
        load_dotenv(config.ENV_FILE_PATH)
        self.api_key = config.OPENAI_API_KEY
        if not self.api_key:
            raise KeyError("The 'config.OPENAI_API_KEY' environment variable is not set.")
        self.gpt_basic_client = OpenAI(api_key=self.api_key)
        self.gpt_client = OpenAI(api_key=config.OPENAI_API_KEY)

    def get_university_name_from_gpt(self, name: str) -> str:
        """
        Retrieves a JSON string containing information about a Canadian university based on a provided identifier.
        The identifier can be the university's name, abbreviation, or an official or Wikipedia URL. The function
        interacts with the OpenAI API to generate a JSON response which includes the university's name, abbreviation,
        official website, and Wikipedia page link.

        Parameters:
        - name (str): The name, abbreviation, or a URL of the university.

        Returns:
        When you are using a quotation, always use double quotation, and NEVER use single quotation.
        Your result should always be directly parsable by json.loads
        - str: A JSON string that includes the university's name, abbreviation, website, and Wikipedia URL.

        Raises:
        - KeyError: If the 'config._OPENAI_KEY' environment variable is not set.
        - OpenAIError: If there is an error in calling the OpenAI API.

        Example:
        - Calling get_university_name_from_gpt("UBC") might return:
            '{"id_":"1","university_name":"The University of British Columbia","abbreviation":"UBC",
            "website":"https://www.ubc.ca","wikipedia":"https://en.wikipedia.org/wiki/University_of_British_Columbia"}'

        Note:
        - The function requires an OpenAI API key to be set in the environment variable 'config._OPENAI_KEY'.
        - This function is specifically designed to use OpenAI's 'gpt-3.5-turbo' model.
        """

        example_output = r"""{"id_":"","university_name":"The University of British Columbia",
        "abbreviation":"UBC","website":"https://www.ubc.ca",
        "wikipedia":"https://en.wikipedia.org/wiki/University_of_British_Columbia"}
        """
        prompt = """# Instruction
        You are an Education developer in Canada aiming to help high school students to apply to universities. Now I will give
        you any university name, an abbreviation, an official website or a wikipedia website that links to the university. You are supposed to give me back
        a JSON filled with fields <university_name>, <abbreviation>, <website>, and <wikipedia>.
        
        You leave the id_ field as is.

        # Suggestion
        You can checkout the Wikipedia
        """
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "UBC"},
            {"role": "assistant", "content": example_output},
            {"role": "user", "content": name},
        ]
        print(f"used GPT: get_university_name_from_gpt, university_name: {name}")
        response = self.gpt_basic_client.chat.completions.create(
            messages=messages, max_tokens=256, model="gpt-3.5-turbo", temperature=0
        )
        return response.choices[0].message.content

    @retry(
        wait=wait_random_exponential(multiplier=1, max=30),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(UnscorableCommentError)
        | retry_if_exception_type(APIConnectionError)
        | retry_if_exception_type(APIError)
        | retry_if_exception_type(RateLimitError)
        | retry_if_exception_type(KeyError)
        | retry_if_exception_type(json.JSONDecodeError),
        reraise=True,  # Reraise the last exception
    )
    def get_value_and_reference_from_gpt(
        self,
        university_name: str,
        target_attribute: str,
        format_: str,
        reference: List[str],
        data_example_pair: str,
        extra_prompt: str = "",
        model: str = config.DEFAULT_OPENAI_MODEL,
        temperature=0,
    ):
        """
        Uses an OpenAI API to fetch specific information about a given university and the associated references from
        internet sources. The function requires details such as the university name and a target attribute that needs
        to be retrieved. It formats the request and sends it to the OpenAI model specified, parsing the JSON response to
        return both the information and its sources. If you don't know or you are not sure, just return "not available"
        without further explaining

        Parameters:
        - university_name (str): Name of the university.
        - target_attribute (str): The specific attribute of the university that needs to be retrieved.
        - format (str): The format expected for the output, as a guide for JSON structure.
        - reference (List[str]): A list of initial references or sources that might contain the required data.
        - data_example_pair (str): Additional examples to guide the model on expected outputs and formats.
        - extra_prompt (str, optional): Additional instructions or context to provide to the model.
        - model (str): Specifies the OpenAI model to use, default is 'gpt-4-turbo'.

        Returns:
        - tuple:
            - output (str): The retrieved value for the specified target attribute.
            - reference (List[str]): A list of URLs or references where the information was sourced.

        Raises:
        - KeyError: If the 'config._OPENAI_KEY' environment variable is not set.
        - OpenAIError: Handles various OpenAI specific exceptions like APIConnectionError, APIError, RateLimitError.

        Usage Example:
        - result = get_value_and_reference_from_gpt(
                "University of British Columbia", "description", "string",
                ["https://en.wikipedia.org/wiki/University_of_British_Columbia"],
                "Example data pairs",
                "Check the latest publications on their official site."
                )
            print(result)
            >>> The University of British Columbia (UBC), located in British Columbia, Canada,
                    is a public university and a member of the U15...
        """

        output_example = r"""{"output": "The University of British Columbia (UBC), located in British Columbia, \
            Canada, is a public university and a member of the U15 Group of Canadian Research Universities, \
                the Association of Commonwealth Universities, the Association of Pacific Rim Universities, \
                    and Universitas 21. As of now, UBC has produced a total of 8 Nobel Prize laureates.", \
                        "reference": ["https://en.wikipedia.org/wiki/University_of_British_Columbia"]}"""
        output_example_graduation_year = (
            r"""{"output": "4", "reference"=["https://you.ubc.ca/applying-ubc/requirements/"]}"""
        )
        prompt = f"""
        # Instruction
        You are an Education developer in Canada aiming to help high school students to apply to universities. Now I will give
        you any university_name, and the target_attribute for you to collect data from the internet, you are supposed to find the knowledge I am looking for and give me back an asserted output.
        If you have checked any websites during your data collection procedure, you should return a List[str], which is a list of references that you have checked.
        Think through the procedure deeply and take it step by step.
        IMPORTANT: You don't need to explain your result, just produce the jsonl as expected, following the exact format.
        If you don't know or you are not sure, just return "not available" without further explaining
        
        # Suggestion
        When you have provided with an official website of the target university, you should value the official website heavily, and check it first.
        {extra_prompt if extra_prompt else ""}
        
        # Extra Reference
        {reference}
        Those are a list of website that you may consider checking against during the data collection.
        
        # Example
        1. ## Input
            university_name: University of British Columbia
            target_attribute: description
            
            ## Output
            {output_example}
            
            ## Logic
            You can find the description of University of British Columbia on wikipedia, you can extra the information from the website, and use the wikipedia page linked to the University of British Columbia as a reference.
        
        2. ## Input
            university_name: University of British Columbia
            target_attribute: graduation_year
            
            ## Output
            {output_example_graduation_year}
        
        # More Example
        Here I will present you with more examples, in the format of a List[str], where each item has the format:
            <university_name>, <target_attribute>, <output>
        ## Examples list
        {data_example_pair}
        Note you are still supposed to output as the output Format.
        
        # Input Format
        university_name: <university_name>
        target_attribute: <target_attribute>
        
        # Output Format
        When you are using a quotation, always use double quotation, and NEVER use single quotation.
        Your result should always be directly parsable by json.loads
        json string format, in the format of 
        output: {format_},
        reference: List[str], which is a list of references that you have checked.
        """

        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"university_name: {university_name}\ntarget_attribute: {target_attribute}",
            },
        ]
        try:
            response = self.gpt_client.chat.completions.create(messages=messages, model=model, temperature=temperature)
            result = response.choices[0].message.content
            # pprint(result)
            print(
                f"used GPT: get_value_and_reference_from_gpt, university_name: {university_name}, \
                    attribute: {target_attribute}"
            )
            result_json = {}
            if isinstance(result, str):
                if result.isdigit():
                    return result, []
                result_json = json.loads(result)
            elif isinstance(result, int):
                result_json = {"output": result, "reference": []}
            return result_json["output"], result_json["reference"]
        except json.JSONDecodeError:
            print(ValueError("Failed to decode JSON from the response."))
            return "", []


__all__ = ["GPTClient"]
# __all__ = ["get_university_name_from_gpt", "get_value_and_reference_from_gpt"]
