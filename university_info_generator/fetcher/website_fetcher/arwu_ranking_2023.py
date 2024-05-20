import json
import threading
from typing import List

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
        # System.setProperty("webdriver.chrome.driver", "C:\\driver\\chromedriver.exe")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.ranking_info = {}
        self.lock = threading.Lock()
        self.df_path = "/home/ivan/Uforse/university_crawl/university_info_generator/fetcher/website_fetcher/ranking_data/arwu_ranking_2023.csv"

    def get_first_page(self, url=ranking_page_url):
        try:
            self.driver.get(f"{url}")
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
        for _ in range(1, self.num_page + 1):
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
        file_path = "/home/ivan/Uforse/university_crawl/university_info_generator/fetcher/website_fetcher/ranking_data/arwu_ranking_2023.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")

    def filter_on_df(self, target_unis: pd.DataFrame):
        if os.path.exists(self.df_path):
            # File exists, load it into a DataFrame
            arwu_data_frame = pd.read_csv(self.df_path)
        else:
            arwu_data_frame = self.to_dataframe()
        # target_uni_canada = pd.read_csv(path_to_csv)
        arwu_data_frame["university_name_lower"] = arwu_data_frame["university_name"].str.lower()
        target_unis["university_name_lower"] = target_unis["university_name"].str.lower()
        column_name = ["canada_id", "arwu_name", "canada_name", "arwu_rank", "arwu_link"]
        matched_df = pd.DataFrame(columns=column_name)
        for _, arwu_row in arwu_data_frame.iterrows():
            arwu_name = arwu_row["university_name_lower"]

            # Check each university in the Canadian DataFrame for a substring match
            for _, canada_row in target_unis.iterrows():
                canada_name = canada_row["university_name_lower"]
                # Check if one name is a substring of the other
                if arwu_name in canada_name or canada_name in arwu_name:
                    # Add the match to the DataFrame
                    matched_df = pd.concat(
                        [
                            matched_df,
                            pd.DataFrame(
                                [
                                    [
                                        canada_row["id_"],
                                        arwu_row["university_name"],
                                        canada_row["university_name"],
                                        arwu_row["rank"],
                                        arwu_row["arwu_uni_link"],
                                    ]
                                ],
                                columns=column_name,
                            ),
                        ],
                        ignore_index=True,
                    )
        matched_df.drop_duplicates(subset=["arwu_name"], keep="first", inplace=True)
        return matched_df

    def get_programs(self, url) -> List[str]:
        def filter_target_table(tables):
            target_tables = list(
                filter(
                    lambda table: "undergraduate programs" in table.select("table > thead > tr > th")[0].string.lower(),
                    tables,
                )
            )
            if target_tables and len(target_tables) > 0:
                return target_tables[0]
            return None

        result_lst = []
        try:
            # page = requests.get(f"{url}")
            # soup = BeautifulSoup(page.content, "html.parser")
            self.driver.get(f"{url}")
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            tables = soup.find_all(name="table")
            target_table = filter_target_table(tables)
            if not target_table:
                return []
            table_soup = BeautifulSoup(str(target_table), "html.parser")
            rows = table_soup.find(
                name="tbody",
            ).find_all(
                name="tr",
            )
            for row in rows:
                result_lst.append(row.string.strip())
        except TimeoutException:
            print("Page load timed out. Check your internet connection or website accessibility.")
        except WebDriverException as e:
            print(f"An error occurred while trying to navigate: {e}")
        if result_lst:
            result_lst = list(set(result_lst))
            result_lst.sort()
        return result_lst

    def get_all_programs(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        # matched_universities[["arwu_name", "arwu_link"]]
        column_name = ["canada_id", "arwu_name", "canada_name", "programs"]
        result_df = pd.DataFrame(columns=column_name)
        for _, row in dataframe.iterrows():
            result_lst = self.get_programs(row["arwu_link"])
            if result_lst:
                row_df = pd.DataFrame(
                            [
                                [
                                    row["canada_id"],
                                    row["arwu_name"],
                                    row["canada_name"],
                                    f"{result_lst}",
                                ]
                            ],
                            columns=column_name,
                        )
                result_df = pd.concat(
                    [
                        result_df,
                        row_df,
                    ],
                    ignore_index=True,
                )
        return result_df
