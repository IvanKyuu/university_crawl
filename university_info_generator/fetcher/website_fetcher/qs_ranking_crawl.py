import time
from pprint import pprint
from typing import Dict

import json
import pandas as pd
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from bs4 import BeautifulSoup


def store_cache(cache_path, cache: Dict[str, str]):
    """
    Stores the provided cache dictionary into a JSON file at the specified path.

    Args:
        cache_path (str): The file path where the cache will be stored.
        cache (dict): The cache data to store.

    Returns:
        None
    """
    with open(cache_path, "w", encoding="utf-8") as cache_file:
        for key, value in cache.items():
            if isinstance(key, tuple):
                key = str(key)

            json_string = json.dumps({key: value}) + "\n"  # Convert to JSON string with newline
            cache_file.write(json_string)


class QSRankingCrawl:
    base_url = "https://www.topuniversities.com"
    ranking_page_url = base_url + "/world-university-rankings&tab=indicators&sort_by=rank&order_by=asc"
    front_url = "https://www.topuniversities.com/world-university-rankings?page="
    back_url = "&tab=indicators&sort_by=rank&order_by=asc"

    def __init__(self, total_num: int = 1498, num_per_page: int = 15):
        self.total_num = total_num
        self.num_per_page = num_per_page
        self.num_page = total_num // num_per_page + 1
        self.driver = webdriver.Chrome(service=Service())
        self.ranking_info = {}

    def get_page_content(self, page_num: int = 0):
        if page_num > self.num_page:
            raise ValueError(f"Expect a page number <= {self.num_page}, but got page_num: {page_num}")
        try:
            self.driver.get(f"{self.front_url}{page_num}{self.back_url}")
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
        soup = BeautifulSoup(page_content, "html.parser")
        rows = soup.find_all(name="div", attrs={"class": "row ind-row firstloaded hide-this-in-mobile-indi"})
        page_data = {}
        for row in rows:
            row_bs = BeautifulSoup(str(row), "html.parser")
            uni_link = row_bs.find(name="a")
            university_name = uni_link.text.strip()
            link = uni_link["href"]
            rank = row_bs.find(name="div", attrs={"class": "_univ-rank mw-100"}).text
            # print(university_name)
            page_data[university_name] = {"rank": rank, "uni_link": f"{self.base_url}{link}"}
            self.ranking_info.update(page_data)
        return page_data

    def get_all_ranking(self):
        for i in range(self.num_page):
            self.parse_page(self.get_page_content(i))

    def close(self):
        if self.driver:
            self.driver.quit()

    def to_dataframe(self):
        data_frame = pd.DataFrame.from_dict(self.ranking_info, orient="index").reset_index()
        data_frame.columns = ["university_name", "rank", "qs_uni_link"]
        return data_frame

    def to_csv(self):
        data_frame = self.to_dataframe()
        file_path = "/home/ivan/Uforse/university_crawl/university_info_generator/fetcher/ranking_fetcher"+"/ranking_data/qs_ranking_2024.csv"
        data_frame.to_csv(file_path, index=False, encoding="utf-8")

