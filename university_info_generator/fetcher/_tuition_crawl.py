"""
This module is designed to facilitate the scraping of tuition fee information for Canadian universities from the website universitystudy.ca. It utilizes the requests library to handle HTTP requests and BeautifulSoup for parsing HTML content. The module provides a class, TuitionCrawl, which offers methods to fetch URLs for specific universities and scrape tuition fee data from those pages.

Classes:
- TuitionCrawl: Manages the scraping of university URLs and tuition fee information.

Dependencies:
- requests: Used to make HTTP requests.
- BeautifulSoup: Used to parse HTML documents.
- collections.defaultdict: Used to manage default values for dictionary keys during scraping.

The TuitionCrawl class includes methods for obtaining the URL of a university's specific page based on the university's name and for scraping the tuition fees from that page. It handles various HTTP errors and parses HTML content to extract relevant data. The class uses predefined HTTP headers to mimic browser requests and avoid being blocked by the website's anti-scraping measures.

Usage:
- Create an instance of the TuitionCrawl class.
- Call the fetch_tuition method with the name of the university to retrieve tuition fee information.

Example:
```python
crawler = TuitionCrawl()
tuition_info = crawler.fetch_tuition('University of Waterloo')
print(tuition_info)
```

"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint
from collections import defaultdict


class TuitionCrawl:
    """
    A class for scraping tuition fee information of Canadian universities from universitystudy.ca.

    Attributes:
    - headers (dict): HTTP headers for the request containing user-agent information.

    Methods:
    - __init__: Initializes a TuitionCrawl object.
    - _get_soup: Sends a request to a URL and returns the parsed HTML content as a BeautifulSoup object.
    - fetch_university_url: Fetches the URL of a university's page based on its name.
    - fetch_tuition: Fetches tuition fee information for a given university.

    Example Usage:
    ```
    crawler = TuitionCrawl()
    tuition_info = crawler.fetch_tuition("University of Waterloo")
    print(tuition_info)
    ```
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "DNT": "1",  # Do Not Track
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self):
        """
        Initializes a TuitionCrawl object.
        """
        return

    def _get_soup(self, url):
        """
        Sends a request to the specified URL and returns the parsed HTML content as a BeautifulSoup object.

        Parameters:
        - url (str): The URL to send the request to.

        Returns:
        - BeautifulSoup: Parsed HTML content as a BeautifulSoup object.
        """
        # Send a request to the main page with a user-agent header
        response = requests.get(url, headers=self.__class__.headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the HTML content of the page to a soup
        return BeautifulSoup(response.text, "html.parser")

    def fetch_university_url(self, university_name: str):
        """
        Fetches the URL of a university's page based on its name.

        Parameters:
        - university_name (str): The name of the university to search for.

        Returns:
        - str: The URL of the university's page if found, otherwise a message indicating the university was not found.
        """
        base_url = "https://universitystudy.ca/canadian-universities/"

        try:
            soup = self._get_soup(base_url)

            # Find all anchor tags, assuming that each university is a link in the page
            links = soup.find_all("a")

            # Filter links that contain the name of the university
            for link in links:
                if link.text.strip().lower() == university_name.lower():
                    # Return the full URL if the university name matches
                    return link["href"]

            return "University not found on the page."
        except requests.RequestException as e:
            return f"An error occurred: {str(e)}"

    def fetch_tuition(self, university_name: str):
        """
        Fetches tuition fee information for a given university.

        Parameters:
        - university_name (str): The name of the university.

        Returns:
        - dict: A dictionary containing tuition fee information for domestic and international students.
                Keys: 'domestic_student_tuition', 'international_student_tuition'.
        """
        try:
            target_url = self.fetch_university_url(university_name)
            soup = self._get_soup(target_url)

            # first find h2 contains TUITION FEES
            h2_lst = soup.find_all("h2")
            target = list(filter(lambda item: "TUITION FEES" in item, h2_lst))
            undergraduate_fees = defaultdict(str)
            if target:
                # from the website, the target elements are just behind "TUITION FEES"
                target_element = target[0]
                current_element = target_element.find_next()
                while current_element and len(undergraduate_fees) < 2:
                    if (
                        "Undergraduate tuition fees" in current_element.text
                        and current_element.span.text not in undergraduate_fees.values()
                    ):
                        undergraduate_fees["fee" + str(len(undergraduate_fees))] = current_element.span.text
                    current_element = current_element.find_next()
            soup = self._get_soup(target_url)
            return {
                "domestic_student_tuition": undergraduate_fees["fee0"],
                "international_student_tuition": undergraduate_fees["fee1"],
            }

        except requests.RequestException as e:
            return f"An error occurred with {university_name}: {str(e)}"

__all__ = []
# if __name__ == "__main__":
#     cra = TuitionCrawl()
#     pprint(cra.fetch_tuition("University of Waterloo"))
#     print("*" * 30)
#     pprint(cra.fetch_tuition("University of Alberta"))
#     print("*" * 30)
