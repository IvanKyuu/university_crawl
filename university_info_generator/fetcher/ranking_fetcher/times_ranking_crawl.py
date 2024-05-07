"""
university_info_generator/fetcher/ranking_fetcher/times_ranking_crawl.py

A web crawler for scraping university rankings from the Times Higher Education website.
"""
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
import pandas as pd

class TimesRankingCrawl:
    """
    A web crawler for scraping university rankings from the Times Higher Education website.

    Attributes:
        base_url (str): The base URL for the Times Higher Education website.
        ranking_page_url (str): The complete URL to the ranking page which includes query parameters for sorting.
        driver (selenium.webdriver.Chrome): Web driver instance to manage browser interactions.
        ranking_info (dict): Dictionary to store the ranking information.
    """
    base_url = "https://www.timeshighereducation.com"
    ranking_page_url = (
        base_url
        + "/world-university-rankings/2024/world-ranking?%2520kan/sort_by/rank/"
        + "sort_order/asc/cols/stats#!/length/-1/sort_by/rank/sort_order/asc/cols/stats"
    )

    def __init__(self):
        """
        Initializes the TimesRankingCrawl with a Chrome WebDriver.
        """
        self.driver = webdriver.Chrome(service=Service())
        self.ranking_info = {}

    def get_page_content(self):
        """
        Navigates to the ranking page and returns the page source.

        Returns:
            str or None: The HTML content of the page or None if an error occurs.
        """
        try:
            self.driver.get(f"{self.ranking_page_url}")
        except TimeoutException:
            print("Page load timed out. Check your internet connection or website accessibility.")
            return None  # or handle as needed
        except WebDriverException as exc:
            print(f"An error occurred while trying to navigate: {exc}")
            return None
        # Full View
        # self.driver.find_element(By.XPATH,'//*[@id="it-will-be-fixed-top"]/div/div[1]/div/ul/li[2]/a').click()
        return self.driver.page_source

    def parse_page(self, page_content):
        """
        Parses the HTML content of a page to extract ranking data.

        Parameters:
            page_content (str): HTML content of the ranking page.

        Returns:
            dict: A dictionary containing the parsed ranking data.
        """
        soup = BeautifulSoup(page_content, "html.parser")
        rows = soup.find_all(name="tr")
        page_data = {}
        for row in rows:
            row_bs = BeautifulSoup(str(row), "html.parser")
            try:
                rank = row_bs.find(name="td", attrs={"class": "rank sorting_1 sorting_2"}).text
                uni_link = row_bs.find(name="a")
                university_name = uni_link.text.strip()
                link = uni_link["href"]
            except AttributeError:
                print("expect got a rank from td, but got none")
                continue
            page_data[university_name] = {"rank": rank, "uni_link": f"{self.base_url}{link}"}
            self.ranking_info.update(page_data)
        return page_data

    def get_all_ranking(self):
        """
        Fetches all ranking data by parsing the ranking page.
        """
        self.parse_page(self.get_page_content())

    def close(self):
        """
        Closes the web driver session.
        """
        if self.driver:
            self.driver.quit()

    def to_dataframe(self):
        """
            Converts ranking information into a pandas DataFrame.

            Returns:
                pd.DataFrame: DataFrame containing ranking information.
        """
        data_frame = pd.DataFrame.from_dict(self.ranking_info, orient="index").reset_index()
        data_frame.columns = ["university_name", "rank", "qs_uni_link"]
        return data_frame

    def to_csv(self):
        """
        Write object to a csv file.
        """
        data_frame = self.to_dataframe()
        file_path = (
            "/home/ivan/Uforse/university_crawl/university_info_generator/fetcher/ranking_fetcher"
            + "/ranking_data/times_ranking_2024.csv"
        )
        data_frame.to_csv(file_path, index=False, encoding="utf-8")
