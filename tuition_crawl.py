import requests
from typing import Any
from bs4 import BeautifulSoup, ResultSet
from pprint import pprint
from collections import defaultdict


class TuitionCrawl:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "DNT": "1",  # Do Not Track
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self):
        pass

    def _get_soup(self, url):
        # Send a request to the main page with a user-agent header
        response = requests.get(url, headers=self.__class__.headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the HTML content of the page to a soup
        return BeautifulSoup(response.text, "html.parser")

    def fetch_university_url(self, university_name: str):
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
            return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    cra = TuitionCrawl()
    pprint(cra.fetch_tuition("University of Waterloo"))
    print("*" * 30)
    pprint(cra.fetch_tuition("University of Alberta"))
    print("*" * 30)
