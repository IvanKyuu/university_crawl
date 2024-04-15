from openai import OpenAI
from openai import APIConnectionError, APIError, RateLimitError
import os
import json
from typing import List
from utility import get_worksheet, restore_by_cache, get_sheet_client, load_cache, store_cache, get_worksheet_records
import gspread
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, retry_if_exception_type, stop_after_attempt


class UnscorableCommentError(Exception):
    pass


cache_repo_path = "./cache_repo"


def get_university_name_from_gpt(name: str) -> str:
    load_dotenv(".env")
    client = OpenAI(api_key=os.environ["IRIS_OPENAI_API_KEY"])
    example_output = r"""{"ID":"","university_name":"The University of British Columbia","abbreviation":"UBC","website":"https://www.ubc.ca","wikipedia":"https://en.wikipedia.org/wiki/University_of_British_Columbia"}"""
    prompt = """# Instruction
    You are an Education developer in Canada aiming to help high school students to apply to universities. Now I will give
    you any university name, an abbreviation, an official website or a wikipedia website that links to the university. You are supposed to give me back
    a JSON filled with fields <university_name>, <abbreviation>, <website>, and <wikipedia>.
    
    You can randomly generate the ID field.

    # Suggestion
    You can checkout the Wikipedia
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "UBC"},
        {"role": "assistant", "content": example_output},
        {"role": "user", "content": name},
    ]
    response = client.chat.completions.create(messages=messages, max_tokens=256, model="gpt-3.5-turbo")
    return response.choices[0].message.content


def get_domestic_tuition_from_gpt(reference: str) -> str:
    load_dotenv(".env")
    client = OpenAI(api_key=os.environ["IRIS_OPENAI_API_KEY"])
    output_format = r"""{domestic_student_tuition: [<min_tuition>, <max_tuition>]}"""
    example_output = r"""{domestic_student_tuition: [7179, 12649]}"""

    prompt = f"""# Instruction
    You are an Education developer in Canada aiming to help high school students to apply to universities. Now I will give
    you a list of website that related to the tuition and fee for new undergraduate in Canada, you are suppose to extra the min and max 
    tuition fee for Canadian citizens and permanent residents.
    
    # Input Format:
    <reference>: List[str], where each item is a string of website you could use to find the tuition from.

    # Output Format:
    json: {output_format}
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "['https://www.torontomu.ca/admissions/tuition-fees/']"},
        {"role": "assistant", "content": example_output},
        {"role": "user", "content": reference},
    ]
    response = client.chat.completions.create(messages=messages, max_tokens=256, model="gpt-3.5-turbo")
    return response.choices[0].message.content


@retry(
    wait=wait_random_exponential(multiplier=1, max=30),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(UnscorableCommentError)
    | retry_if_exception_type(APIConnectionError)
    | retry_if_exception_type(APIError)
    | retry_if_exception_type(RateLimitError)
    | retry_if_exception_type(KeyError),
    reraise=True,  # Reraise the last exception
)
def get_value_and_reference_from_gpt(
    university_name: str,
    target_attribute: str,
    format: str,
    reference: List[str],
    data_example_pair: str,
    extra_prompt: str = "",
    model: str = "gpt-4-turbo",
):
    output_example = r"""{output: 'The University of British Columbia (UBC), located in British Columbia, Canada, is a public university and a member of the U15 Group of Canadian Research Universities, the Association of Commonwealth Universities, the Association of Pacific Rim Universities, and Universitas 21. As of now, UBC has produced a total of 8 Nobel Prize laureates.', reference: ['https://en.wikipedia.org/wiki/University_of_British_Columbia']}"""
    output_example_graduation_year = r"""{output: '4', reference=['https://you.ubc.ca/applying-ubc/requirements/']}"""
    prompt = f"""
    # Instruction
    You are an Education developer in Canada aiming to help high school students to apply to universities. Now I will give
    you any university_name, and the target_attribute for you to collect data from the internet, you are supposed to find the knowledge I am looking for and give me back an asserted output.
    If you have checked any websites during your data collection procedure, you should return a List[str], which is a list of references that you have checked.
    Think through the procedure deeply and take it step by step.
    You don't need to explain your result, just produce the jsonl as expected.
    
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
    json format, in the format of 
    output: {format},
    reference: List[str], which is a list of references that you have checked.
    """

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""},
        {
            "role": "user",
            "content": f"university_name: {university_name}\ntarget_attribute: {target_attribute}",
        },
    ]
    client = OpenAI(api_key=os.environ["IRIS_OPENAI_API_KEY"])
    response = client.chat.completions.create(messages=messages, model=model)
    result = response.choices[0].message.content
    # pprint(f"GPT: {result}")
    result_json = json.loads(result)
    return result_json["output"], result_json["reference"]


def fill_missing_entry(records, columns: List[str], sheet):
    for index, record in enumerate(records, start=2):
        parameter = None
        for column_name in columns[1:]:
            if record[column_name]:
                parameter = record[column_name]
                break

        if not parameter:
            continue

        # use gpt to fill the data
        missing_data_json = get_university_name_from_gpt(parameter)
        missing_data = json.loads(missing_data_json)

        for column_index, column_name in enumerate(columns):
            if not record[column_name]:
                sheet.update_cell(index, column_index + 1, missing_data[column_name])


def fill_target_university():
    sheet = gspread.Client = get_worksheet("target_university")
    cache = load_cache(os.path.join(cache_repo_path, "target_university_before_action.jsonl"))
    records = cache["target_university"]
    column_names = sheet.row_values(1)
    fill_missing_entry(records, column_names, sheet)
    return get_worksheet_records("target_university")
