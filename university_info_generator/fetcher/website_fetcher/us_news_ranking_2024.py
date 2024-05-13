import time
from typing import List

import json
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

import threading


class USNewsRankingCrawl:
    base_url = "https://www.usnews.com"
    ranking_page_url = base_url + "/education/best-global-universities/search"
    front_url = "?name="
    # back_url = "&country=api&subject=search"

    def __init__(self, total_num: int = 2165):
        self.total_num = total_num
        self.driver = webdriver.Chrome(service=Service())
        self.ranking_info = {}
        self.lock = threading.Lock()

    # TODO: fix this, can't load all pages, dynamically, at once
    def keep_scrolling_to_the_bottom(self):
        while True:
            previous_scrollY = self.driver.execute_script("return window.scrollY")
            self.driver.execute_script("window.scrollBy( 0, 230 )")
            time.sleep(10)
            if previous_scrollY == self.driver.execute_script("return window.scrollY"):
                button = self.driver.find_element(
                    By.CSS_SELECTOR, "#rankings > div.pager__Container-sc-1i8e93j-0.hqeWub > button"
                )
                button.click()
                time.sleep(2)
                if previous_scrollY == self.driver.execute_script("return window.scrollY"):
                    break

    def get_page_content_by_name(self, name: str):
        if not name:
            raise ValueError("Expect the name of a university but got none.")
        try:
            self.driver.get(f"{self.ranking_page_url}{self.front_url}{name}")
        except TimeoutException:
            print("Page load timed out. Check your internet connection or website accessibility.")
            return None  # or handle as needed
        except WebDriverException as exc:
            print(f"An error occurred while trying to navigate: {exc}")
            return None
        return self.driver.page_source

    def parse_page(self, page_content):
        page_data = {}
        soup = BeautifulSoup(page_content, "html.parser")
        try:
            rows = soup.find_all(name="li", attrs={"class": "item-list__ListItemStyled-sc-18yjqdy-1 boZDDO"})
        except AttributeError:
            return None
        for row in rows:
            with self.lock:
                row_bs = BeautifulSoup(str(row), "html.parser")
                try:
                    rank = row_bs.find(
                        name="div", attrs={"class": "RankList__Rank-sc-2xewen-2 ieuiBj ranked has-badge"}
                    ).text.strip()
                    uni_link = row_bs.find(
                        name="a",
                        attrs={
                            "class": "Anchor-byh49a-0 DetailCardGlobalUniversities__StyledAnchor-sc-1v60hm5-5 eMEqFO bFdMFJ"
                        },
                    )
                    university_name = uni_link.text.strip()
                    link = uni_link["href"]
                    if "#" in rank:
                        rank = rank[rank.index("#") + 1 :]
                except AttributeError:
                    print("Not enough info skipped\n" + str(row))
                    continue
                page_data[university_name] = {"rank": rank, "uni_link": f"{link}"}
                # print(page_data[university_name])

                self.ranking_info.update(page_data)
        return page_data

    def get_all_ranking_by_list(self, target_lst: List[str]):
        for uni_name in target_lst:
            with self.lock:
                self.parse_page(self.get_page_content_by_name(uni_name))
                self.driver.manage().deleteAllCookies()

    def close(self):
        if self.driver:
            self.driver.quit()

    def to_dataframe(self):
        df = pd.DataFrame.from_dict(self.ranking_info, orient="index").reset_index()
        df.columns = ["university_name", "rank", "arwu_uni_link"]
        return df

    def to_csv(self):
        df = self.to_dataframe()
        file_path = "/home/ivan/Uforse/university_crawl/university_info_generator/fetcher/ranking_fetcher/ranking_data/us_news_ranking_2023.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")
