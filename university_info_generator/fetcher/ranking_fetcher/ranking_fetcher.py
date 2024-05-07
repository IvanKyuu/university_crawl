from typing import Literal, Dict, List, Optional

import pandas as pd
import numpy as np
from selenium.common.exceptions import TimeoutException

from configs.config import PROJECT_HOME

__all__ = ["RankingFetcher"]


class RankingFetcher:
    repo_path = f"{PROJECT_HOME}/university_info_generator/fetcher/ranking_fetcher/"

    def __init__(self):
        self.ranking_arwu_rank_2023_df = pd.read_csv(f"{self.repo_path}/ranking_data/arwu_ranking_2023.csv")
        self.ranking_qs_news_2024_df = pd.read_csv(f"{self.repo_path}/ranking_data/qs_ranking_2024.csv")
        self.ranking_times_rank_2024_df = pd.read_csv(f"{self.repo_path}/ranking_data/times_ranking_2024.csv")
        self.ranking_us_news_2023_df = pd.read_csv(f"{self.repo_path}/ranking_data/us_news_ranking_2023.csv")

    def get_ranking(
        self,
        university_name: str,
        ranking_type: Literal[
            "ranking_qs_news_2024", "ranking_us_news_2023", "ranking_times_rank_2024", "ranking_arwu_rank_2023"
        ],
    ) -> Optional[Dict[str, str]]:
        if ranking_type in (
            "ranking_qs_news_2024",
            "ranking_times_rank_2024",
            "ranking_arwu_rank_2023",
            "ranking_us_news_2023",
        ):
            df_name = ranking_type + "_df"
            dataframe = getattr(self, df_name)
            filtered_df = dataframe[dataframe["university_name"].str.contains(university_name, case=False, na=False)]
            dicts = filtered_df.to_dict("records")
            if len(dicts) != 1:
                return None
            return dicts[0]


if __name__ == "__main__":
    ran_fe = RankingFetcher()
    print(ran_fe.get_ranking("University of Toronto", "ranking_us_news_2023"))
