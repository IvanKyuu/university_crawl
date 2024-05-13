import pandas as pd
import os
from typing import Dict


class USNewsParser:
    def load_usnews_csv(self, file_path: str):
        if not os.path.exists(file_path):
            return None
        dataframe = pd.read_csv(file_path)
        return dataframe

    def __init__(self):
        self.us_df = self.load_usnews_csv("data-detailed.csv")

    def initialize_data(university_name: str) -> Dict[str, str]:
        pass
