import json
import threading

import pandas as pd

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

class ARWURankingCrawl:
    base_url = "https://www.shanghairanking.com"
    ranking_page_url = base_url + "/rankings/arwu/2023"

    def __init__(self, total_num: int = 1000, num_per_page: int = 30):
        self.total_num = total_num
        self.num_per_page = num_per_page
        self.num_page = total_num // num_per_page + 1
        self.driver = webdriver.Chrome(service=Service())
        self.ranking_info = {}
        self.lock = threading.Lock()

    def get_first_page(self):
        try:
            self.driver.get(f"{self.ranking_page_url}")
        except TimeoutException:
            print("Page load timed out. Check your internet connection or website accessibility.")
            return None  # or handle as needed
        except WebDriverException as e:
            print(f"An error occurred while trying to navigate: {e}")
            return None
        # Full View
        # self.driver.find_element(By.XPATH,'//*[@id="it-will-be-fixed-top"]/div/div[1]/div/ul/li[2]/a').click()
        return self.driver.page_source

    def get_page_content(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "#content-box > ul > li.ant-pagination-next").click()
        except TimeoutException:
            print("Page load timed out. Check your internet connection or website accessibility.")
            return None  # or handle as needed
        except WebDriverException as e:
            print(f"An error occurred while trying to navigate: {e}")
            return None
        return self.driver.page_source

    def parse_page(self, page_content):
        page_data = {}
        soup = BeautifulSoup(page_content, "html.parser")
        rows = soup.find_all(name="tr")
        for row in rows[-self.num_per_page :]:
            # print(row)
            row_bs = BeautifulSoup(str(row), "html.parser")
            try:
                rank = row_bs.find(name="div", attrs={"class": "ranking"}).text.strip()
                link = row_bs.find(name="a")["href"]
                university_name = row_bs.find(name="span", attrs={"class": "univ-name"}).text.strip()
            except AttributeError:
                print("Not enough info skipped\n" + str(row))
                continue
            page_data[university_name] = {"rank": rank, "uni_link": f"{self.base_url}{link}"}
            # print(page_data[university_name])
            self.ranking_info.update(page_data)
        return page_data

    def get_all_ranking(self):
        with self.lock:
            self.parse_page(self.get_first_page())
        for i in range(1, self.num_page + 1):
            with self.lock:
                self.parse_page(self.get_page_content())

    def close(self):
        if self.driver:
            self.driver.quit()

    def to_dataframe(self):
        df = pd.DataFrame.from_dict(self.ranking_info, orient="index").reset_index()
        df.columns = ["university_name", "rank", "arwu_uni_link"]
        return df

    def to_csv(self):
        df = self.to_dataframe()
        file_path = "/home/ivan/Uforse/university_crawl/university_info_generator/fetcher/ranking_fetcher/ranking_data/arwu_ranking_2023.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")
