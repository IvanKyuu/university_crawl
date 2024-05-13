"""
This module, _lanchain_method, defines the LanchainWrapper class that facilitates the interaction between
    the Langchain API and our modules. It provides specialized methods to retrieve and process university-related
    data through advanced API calls and AI-driven processing.

The LanchainWrapper class within this module utilizes
        LangChain's Tavily Search API and OpenAI's GPT models
    to perform detailed searches and generate responses based on structured prompts.
    These functionalities are critical for retrieving specific attributes and rankings of universities
            with high accuracy and contextual relevance.

Key Components:
- LanchainWrapper: A class that serves as an interface to the Langchain API, encapsulating methods that leverage
    both the Tavily Search API and OpenAI GPT models to fetch and format university data as per user-defined criteria.

Class Functionalities Provided:
- get_retrieved_attr_with_format_tavily: the method in the LanchainWrapper allow for fetching detailed
    university attributes such as faculty information, tuition fees, etc., using custom prompts and AI models.
- get_retrieved_ranking_with_format_tavily: the method ranking data from specified references,
    processing this information through GPT models to ensure the relevance and accuracy of the output.

Use Cases:
- The module is primarily used in scenarios where detailed and reliable university data is required
    for analytical or informational purposes within the educational sector of a more general module.
- It supports dynamic data retrieval for user queries regarding university rankings and specific attributes,
    enhancing the user experience by providing timely and contextually relevant information.

This module is an integral part of the university information scrapping, interacting with other modules that
    handle data preparing, cleaning and generations.
"""

from pprint import pprint
import os
from typing import List, Any, Literal, Dict
import re
import json

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, ConnectionError
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_random_exponential

from langchain_chroma import Chroma
from langchain_core.documents.base import Document
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from university_info_generator.configs import config
from university_info_generator.configs.enum_class import UniversityAttributeColumnType

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY

__all__ = ["LanchainWrapper"]


class LanchainWrapper:
    """
    A wrapper class for Langchain operations that retrieve and process university-related information
        using the Langchain API and LLMs.

    This class provides methods to retrieve attributes and rankings of universities by leveraging:
            Tavily's search API
            GPT models
        for contextual retrieval and generation of responses based on structured prompts.
    """

    def __init__(self) -> None:
        pass

    @classmethod
    @retry(
        stop=stop_after_attempt(3),  # Stop after 3 attempts
        wait=wait_random_exponential(multiplier=1, max=30),
        retry=retry_if_exception_type((HTTPError, ConnectionError)),  # Retry on HTTPError and ConnectionError
        reraise=True,
    )
    def get_retrieved_attr_with_format_tavily(
        cls,
        university_name: str,
        target_attribute: str,
        format_: str,
        reference: List[str],
        _data_example_pair: str,
        _extra_prompt: str = "",
        k_value: int = UniversityAttributeColumnType.K_VALUE.get_default_value(),
        _params=None,
    ):
        """
        Retrieves detailed attributes for a specified university using the
                Tavily search API
                structured OpenAI prompts
            in a data pipeline.

        Parameters:
            university_name (str): The name of the university for which to retrieve information.
            target_attribute (str): The specific attribute of the university to retrieve.
            format_ (str): The desired output format for the retrieved information.
            reference (List[str]): A list of references in terms of URLs to consider when retrieving information.
            data_example_pair (str): Example data to help guide the retrieval process.
            extra_prompt (str, optional): Additional instructions or context for the OpenAI prompt.

        Returns:
            The retrieved information as processed by the GPT model in the specified format.

        Usage:
            This method is used when precise, detailed information about a university's specific attributes is required.
                It constructs a detailed query using multiple inputs to obtain accurate and relevant information.
        """
        print(
            f"""used langchain: get_retrieved_attr_with_format_tavily, university_name: {university_name},
                attribute: {target_attribute}"""
        )
        retriever = TavilySearchAPIRetriever(api_key=config.TAVILY_API_KEY, k=k_value)
        # GPT
        prompt = ChatPromptTemplate.from_template(
            """Find the attribute based only on the context provided.
                If you don't know or you are not sure, just return "not available" without further explaining
                You will only use information that related to the {university_name}.
                You can check here for additional reference: {reference}.
                {extra_prompt}
                Context: {context}
                Attribute: {attribute}
                Output format: {format}
                Output example: {example}
                """
        )

        # Context is the part that retriever get to work

        chain = (
            RunnablePassthrough.assign(
                context=(
                    # Tavily
                    lambda x: "For "
                    + x["university_name"]
                    + ". "
                    + x["extra_prompt"]
                    # + "You may wish to refer "
                    # + x["reference"]
                    + "\n If you find the website that you are referring from the university, "
                    + " load the whole page directly"
                )
                | retriever
            )
            | prompt
            | ChatOpenAI(
                api_key=config.OPENAI_API_KEY,
                model=config.DEFAULT_OPENAI_MODEL,
                temperature=0,
            )
            | StrOutputParser()
        )

        return chain.invoke(
            {
                "university_name": f"{university_name}",
                "reference": f"{reference}",
                "example": f"{_data_example_pair}",
                "extra_prompt": f"{_extra_prompt}",
                "attribute": f"{target_attribute}",
                "format": f"{format_}",
            }
        )

    @classmethod
    @retry(
        stop=stop_after_attempt(3),  # Stop after 3 attempts
        wait=wait_random_exponential(multiplier=3, max=30),
        retry=retry_if_exception_type((HTTPError, ConnectionError)),  # Retry on HTTPError and ConnectionError
        reraise=True,
    )
    def get_retrieved_ranking_with_format_tavily(
        cls,
        university_name: str,
        target_attribute: str,
        format_: str,
        reference: List[str],
        _data_example_pair: str,  #                   place holder: data_example_pair
        _extra_prompt: str = "",  #                   place holder: extra_prompt
        k_value: int = UniversityAttributeColumnType.K_VALUE.get_default_value(),
        _params=None,
    ):
        """
        Retrieves ranking information for a specified university using
                Tavily search API
                structured OpenAI prompts.

        Parameters:
            university_name (str): The name of the university for which to retrieve ranking information.
            target_attribute (str): The specific ranking attribute to retrieve (e.g., QSNews, USNews, ARWU).
            format_ (str): The desired output format for the ranking information.
            reference (List[str]): A list of URLs where the latest ranking information can be found.

        Returns:
            The retrieved ranking information as processed by the GPT model in the specified format.

        Usage:
            This method is used when accurate and current ranking information about a university is required.
                It leverages specific references to provide the latest results from reliable ranking publications.
        """
        print(
            f"""used langchain: get_retrieved_ranking_with_format_tavily, university_name: {university_name},
                attribute: {target_attribute}"""
        )

        retriever = TavilySearchAPIRetriever(api_key=config.TAVILY_API_KEY, k=k_value)
        prompt = ChatPromptTemplate.from_template(
            """Find the ranking based only on the context provided.
                If you don't know or you are not sure, just return "not available" without further explaining.
                You can check here: {reference}.
                Focus on the latest results from these websites.
        Context: {context}
        Attribute: {attribute} of {university_name}
        output format: {format}"""
        )

        chain = (
            RunnablePassthrough.assign(
                context=(
                    lambda x: "For "
                    + x["university_name"]
                    + " "
                    + x["attribute"]
                    + ". You may wish to refer "
                    + x["reference"]
                )
                | retriever
            )
            | prompt
            | ChatOpenAI(
                api_key=config.OPENAI_API_KEY,
                model=config.DEFAULT_OPENAI_MODEL,
                temperature=0,
            )
            | StrOutputParser()
        )

        return chain.invoke(
            {
                "university_name": f"{university_name}",
                "reference": f"{reference}",
                "attribute": f"{target_attribute}",
                "format": f"{format_}",
            }
        )

    @classmethod
    def get_text_from_url(cls, url: str, params: Dict[str, Any]) -> str:
        """
        return fetched text from a specific url

        TODO: make this better
        """

        # Clean text function
        def clean_text(html_content):
            return re.sub(r"\s+", " ", html_content).strip()

        trans = params["transformer"]
        pprint(f"fetch with {trans} from: {url}")
        if trans == "BeautifulSoup":
            html_content = BeautifulSoup(url, "html.parser").text
            cleaned_content = clean_text(html_content)
        elif trans == "RecursiveURL":
            web_pages = RecursiveUrlLoader(
                url=url, max_depth=1, extractor=lambda x: BeautifulSoup(x, "html.parser").text
            ).load()
            cleaned_content = []
            for page in web_pages:
                cleaned_content.append(clean_text(page.page_content))
            cleaned_content = "\n".join(cleaned_content)
        return cleaned_content

    @classmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=1, max=30),
        retry=retry_if_exception_type((HTTPError, ConnectionError)),
        reraise=True,
    )
    def get_retrieved_attr_langchain_google_search(
        cls,
        university_name: str,
        target_attribute: str,
        format_: str,
        reference: List[str],
        _data_example_pair: str,
        _extra_prompt: str = "",
        k_value: int = UniversityAttributeColumnType.K_VALUE.get_default_value(),
        _params: Dict[Literal["transformer"], Literal["BeautifulSoup", "RecursiveURL"]] = {
            "transformer": "BeautifulSoup"
        },
    ):
        """
        Retrieves attributes for a specified university by performing an automated Google search
        and then using language models to synthesize information from retrieved documents.

        Args:
            university_name (str): Name of the university.
            target_attribute (str): The attribute to retrieve.
            format_ (str): The desired output format.
            reference (Union[List[str], str]): List of references or a single reference URL.
            _data_example_pair (str): Example data to help guide the retrieval process.
            _extra_prompt (str, optional): Additional prompt information for the model.
            k_value (int, optional): Number of search results to consider.

        Returns:
            The synthesized information as a string.
        """

        print(f"Searching for {target_attribute} related to {university_name} using LangChain and Google search.")

        # Set up search API
        search = GoogleSerperAPIWrapper(k=k_value, gl="ca", serper_api_key=config.SERPER_API_KEY, type="search")
        links = []
        # print(reference)
        if isinstance(reference, str):
            reference = json.loads(reference.replace("'", '"'))
        # print(f"{reference}")
        for site in reference:
            # print(f"in for {site}")
            results = search.results(f"{target_attribute} {university_name} site={site}")
            links.extend([result["link"] for result in results.get("organic", [])])
        # print(links)

        # Fetch documents from links and clean them
        docs = []
        for url in set(links):
            doc = __class__.get_text_from_url(url=url, params=_params)
            # pprint(f"   type: {type(doc)}")
            docs.append(doc)

        # Prepare and execute the model chain
        template = """
        Find the attribute based only on the context provided.
        If you don't know or you are not sure, just return "not available" without further explaining
        Find detailed information about {target_attribute} from {university_name} from the context:
        Context: {context}
        {extra_prompt}
        Output format: {format}
        Example: {example}
        """
        prompt = ChatPromptTemplate.from_template(template)
        # response = ChatOpenAI(api_key=config.OPENAI_API_KEY, model=config.DEFAULT_OPENAI_MODEL, temperature=0).invoke(
        #     prompt
        # )
        chain = (
            RunnablePassthrough()
            | prompt
            | ChatOpenAI(
                api_key=config.OPENAI_API_KEY,
                model=config.DEFAULT_OPENAI_MODEL,
                temperature=0,
            )
            | StrOutputParser()
        )
        return chain.invoke(
            {
                "university_name": f"{university_name}",
                # "reference": f"{reference}",
                "example": f"{_data_example_pair}",
                "extra_prompt": f"{_extra_prompt}",
                "target_attribute": f"{target_attribute}",
                "format": f"{format_}",
                "context": f"{' '.join(docs)}",
            }
        )
