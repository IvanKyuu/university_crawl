import pandas as pd
import os
from typing import Dict


class USNewsParser:

    def __init__(self):
        def load_usnews_csv(file_path: str):
            if not os.path.exists(file_path):
                return None
            dataframe = pd.read_csv(file_path)
            return dataframe

        self.us_df = load_usnews_csv(
            "/home/ivan/Uforse/university_crawl/university_info_generator/fetch_logic/all_university_usa.csv"
        )

    def initialize_data(self, university_name: str) -> Dict[str, str]:
        result_row: pd.DataFrame = self.us_df.loc[(self.us_df.get("institution.displayName") == university_name)]
        if result_row.empty:
            return None
        university_type = ""
        if "public" in result_row["institution.institutionalControl"].str.lower():
            university_type += "public"
        else:
            university_type += "private"
        if len(university_type) > 0:
            university_type += " "
        if "university" in result_row["institution.schoolType"].str.lower():
            university_type += "university"
        else:
            university_type += "college"
        # rank_val := int(result_row["ranking.sortRank"])
        if (rank_val := result_row["ranking.sortRank"].iloc[0]) > 0:
            rank = str(rank_val)
        else:
            rank = ""
        ret_json = {"university_type": university_type, "ranking_us_news_2023": rank}
        if rank or university_type:
            ret_json["university_name"] = university_name
        return ret_json


if __name__ == "__main__":
    up = USNewsParser()
    # pd.read_csv("/home/ivan/Uforse/university_crawl/university_info_generator/fetch_logic/data-detailed.csv")
    print(up.initialize_data("University of Massachusetts--Amherst"))
    df = up.us_df
    df.to_csv(
        "/home/ivan/Uforse/university_crawl/university_info_generator/fetch_logic/all_universities_usa.csv",
        columns=["id_", "institution.displayName"], index=False
    )
