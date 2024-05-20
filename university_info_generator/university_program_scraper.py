from typing import Optional, List, Dict, Literal
from collections import defaultdict
import time

import pandas as pd
import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet, PageElement
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

from pprint import pprint

from university_info_generator.configs.config import PROJECT_HOME
from program import Program

__all__ = ["UniversityProgramScraper"]


class UniversityProgramScraper:
    data_repo_path = f"{PROJECT_HOME}/university_info_generator/data"
    base_url = "https://www.topuniversities.com"
    program_url = f"{base_url}/programs"
    filter_index_dict = {"subject": 4, "study_level": 3}

    def __init__(self, need_scrap=False, country: Literal["US", "CA"] = "CA") -> None:
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")
        # self.driver = webdriver.Chrome(chrome_options)
        service = Service(
            "/usr/bin/chromedriver/chromedriver"
        )  # Make sure to replace this with the correct path to your chromedriver
        self.driver = None
        if need_scrap:
            self.driver = webdriver.Chrome(service=service)
            # chrome_options = Options()
            # chrome_options.add_argument("--headless")
            # chrome_options.add_argument("--no-sandbox")
            # self.driver = webdriver.Chrome(chrome_options)
        self.uni_link_df = None
        if country == "CA":
            self.uni_link_df = pd.read_csv(f"{self.data_repo_path}/canada_dataset/qs_canada_uni_matched.csv")
        else:
            # country == "US"
            self.uni_link_df = pd.read_csv(f"{self.data_repo_path}/data/usa_dataset/qs_usa_uni_matched.csv")

    def get_entry_page(self):
        self.driver.get(f"{self.program_url}")
        return self

    def get_filter_lst(self, index) -> Optional[List[str]]:
        result_lst = None
        self.get_entry_page()
        # input_button = self.driver.find_element(By.XPATH, '//*[@id="_filtersforListingQS"]/div/div[1]/div/div[4]')
        label = WebDriverWait(self.driver, 3).until(
            EC.visibility_of_element_located(
                (By.XPATH, f'//*[@id="_filtersforListingQS"]/div/div[1]/div/div[{index+1}]/div[2]/div/div/label')
            )
        )
        label_text = label.text
        ActionChains(self.driver).move_to_element(label).pause(1).click().perform()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        filter_options: PageElement = soup.find(name="div", attrs={"class": "_university_fliters_div"})
        filter_lst: ResultSet = filter_options.find_all_next(name="div", attrs={"class": "col-lg-3"})
        study_level_filter = filter_lst[index]
        study_level_soup = BeautifulSoup(str(study_level_filter), "html.parser")
        rows: ResultSet = study_level_soup.find_all(name="option")
        result_lst = []
        for row in rows:
            if row.text == label_text:
                continue
            result_lst.append(row.text)

        return result_lst

    def get_study_level_lst(self) -> Optional[List[str]]:
        return self.get_filter_lst(index=self.filter_index_dict["study_level"])

    def get_subject_lst(self):
        return self.get_filter_lst(index=self.filter_index_dict["subject"])

    def add_input(self, input_str: str):
        input_bar = self.driver.find_element(By.XPATH, '//*[@id="search_global"]')
        ActionChains(self.driver).send_keys_to_element(input_bar, input_str.strip()).pause(1).send_keys_to_element(
            input_bar, Keys.ENTER
        ).pause(3).perform()
        return self

    def get_program_link_lst(self, link: str) -> Dict[str, Dict[str, Dict[str, str]]]:
        program_lst: Dict[str, Dict[str, Dict[str, str]]] = {}
        try:
            self.driver.get(link)
            dpt_tabs = self.driver.find_element(By.ID, "aptabs")
            dpt_lst = dpt_tabs.find_elements(By.TAG_NAME, "h3")
            for dpt in dpt_lst:
                program_lst[dpt.text.lower()] = {}
            panel_group_by_dpt = self.driver.find_elements(By.CLASS_NAME, "panel-group")
            assert len(panel_group_by_dpt) == len(program_lst)
            for each_group, dpt in zip(panel_group_by_dpt, program_lst):
                soup = BeautifulSoup(each_group.get_attribute("outerHTML"), "html.parser")
                subject_areas: ResultSet = soup.find_all(
                    name="div", attrs={"class": "item", "data-once": "qs_profiles"}
                )

                subject_area: Tag
                for subject_area in subject_areas:
                    department_name = subject_area.find(name="span", attrs={"class": "pgmname"}).text
                    program_lst[dpt].update({department_name: {}})
                    programs = subject_area.find(name="div", attrs={"class": "item-body"}).find_all(
                        name="div", attrs={"class": "views-row"}
                    )
                    program_body: Tag
                    for program_body in programs:
                        program_name: str = program_body.find(name="h4").text
                        program_link = program_body.find(name="a", attrs={"id": "view_details"}).get("href")
                        program_lst[dpt][department_name].update({program_name.strip(): self.base_url + program_link})
        except NoSuchElementException:
            pass
        return program_lst

    def extract_program_by_link(self, link: str, program=Program()) -> Program:
        # result_program = Program()
        try:
            self.driver.get(link)
            page_soup = BeautifulSoup(self.driver.page_source, "html.parser")
            # print(page_soup)
            univ_log_div = page_soup.find(name="div", attrs={"class": "univ-logo-n-name"}, recursive=True)
            univ_log_soup = BeautifulSoup(str(univ_log_div), "html.parser")
            # print("*" * 80)
            badge_description_lst: Tag = page_soup.find_all(
                name="div", attrs={"class": "badge-description"}, recursive=True
            )

            # extract QS Subject Rankings / program duration / Tuition Fee/year / Main Subject Area
            rank = ""
            duration = ""
            main_subject = ""
            if badge_description_lst:
                for badge in badge_description_lst:
                    badge_soup = BeautifulSoup(str(badge), "html.parser")
                    h3_lst = badge_soup.h3.contents
                    if len(h3_lst) == 3 and "rank" in h3_lst[2].text.lower():
                        rank = h3_lst[1]
                    if len(h3_lst) == 2:
                        if "duration" in h3_lst[1].text.lower():
                            duration = int(list(h3_lst[0].split("month"))[0])
                            duration //= 12
                        if "main subject" in h3_lst[1].text.lower():
                            main_subject = h3_lst[0].text.lower()

            # extract Main Subject / Degree / Study Level / description
            degree_type = ""
            academic_degree_level = ""
            description = ""
            car_content_div: Tag = page_soup.find(name="div", attrs={"class": "card-content"})
            if car_content_div:
                card_content_lst = car_content_div.find_all(name="div", attrs={"class": "prog-view-highli"})

                if card_content_lst:
                    for card_content in card_content_lst:
                        if "main subject" in card_content.h3.text.lower():
                            if not main_subject:
                                main_subject = card_content.p
                        elif "degree" in card_content.h3.text.lower():
                            degree_type = card_content.p.text
                        elif "study level" in card_content.h3.text.lower():
                            academic_degree_level = card_content.p.text.lower()
                    description_div: Tag = car_content_div.find(
                        name="div", attrs={"class": "textsection abt-overview-read"}
                    )
                    if description_div and len(description_div.contents):
                        description += description_div.contents[0].text.strip()
                    if detail := description_div.find(name="span", attrs={"class": "details"}):
                        description += " " if description else "" + detail.contents[0].text.strip()

            # admin requirement
            # extra language / course_requirement
            enrollment_language_requirement = ""
            course_requirement = ""
            admin_div: Tag = page_soup.find(name="div", attrs={"id": "p2-university-information"})

            if admin_div:
                language_div_lst = admin_div.find_all(
                    name="div", attrs={"class": "univ-subsection-full-width-value bottom-div"}
                )
                for language_div in language_div_lst:
                    if "TOEFL" in language_div.label.text.upper():
                        enrollment_language_requirement += f"TOEFL: {language_div.div.text}"
                    if "IELTS" in language_div.label.text.upper():
                        if enrollment_language_requirement:
                            enrollment_language_requirement += "\n"
                        enrollment_language_requirement += f"IELTS: {language_div.div.text}"
            course_req_div = admin_div.find(name="div", attrs={"class": "exam-score-footnote"})
            if course_req_div:
                if course_req_div.p:
                    course_requirement = course_req_div.p.text
                    course_requirement = course_requirement.replace(":", ":\n").replace(";", ";\n")

            # extract tuition fee
            def process_fee(fee: str):
                fee_num, fee_type = fee.upper().split()
                return f"{fee_type.strip()} ${fee_num.strip()}"

            domestic_fee = ""
            international_fee = ""
            tuition_div = page_soup.find(name="div", attrs={"id": "p2-tuition-fee-and-scholarships"})
            if tuition_div:
                tuition_lst = tuition_div.find_all(name="div", attrs={"class": "univ-subsection"})
                if tuition_lst:
                    tui_div: Tag
                    for tui_div in tuition_lst:
                        if "domestic" in tui_div.h4.text.lower():
                            domestic_fee = tui_div.find(name="div", attrs={"class": "univ-subsection-value"})
                            domestic_fee = process_fee(domestic_fee.div.text)
                        if "international" in tui_div.h4.text.lower():
                            international_fee = tui_div.find(name="div", attrs={"class": "univ-subsection-value"})
                            international_fee = process_fee(international_fee.div.text)
            program.update(
                {
                    "program_name": univ_log_soup.find(
                        name="h1",
                    ).text,
                    "location": univ_log_soup.find(name="h2", attrs={"class": "hero-campus-heading"}).text,
                    "ranking_qs_subject_2024": rank,
                    "graduation_year": duration,
                    "main_subject_area": main_subject,
                    "degree_type": degree_type,
                    "academic_degree_level": academic_degree_level,
                    "description": description,
                    "enrollment_language_requirement": enrollment_language_requirement,
                    "course_requirement": course_requirement,
                    "domestic_student_tuition": domestic_fee,
                    "international_student_tuition": international_fee,
                }
            )
        except NoSuchElementException:
            pass
        return program

    @staticmethod
    def join_df(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        save_path: str = f"{PROJECT_HOME}/university_info_generator/data/canada_dataset/qs_canada_uni_matched.csv",
    ):
        result = df1.set_index("university_name").join(
            df2.set_index("university_name"), on="university_name", how="inner"
        )
        result.to_csv(save_path)
        return result

    def close(self):
        if self.driver:
            self.driver.quit()
