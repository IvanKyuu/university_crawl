from typing import Dict, List
import json

__all__ = ["Program"]


class Program:
    en_ch_translation_map = {
        "program_id": "program_id",
        "university_id": "学校id",
        "university_name": "学校",
        "main_subject_area": "主要学科领域",  # done
        "program_name": "专业名",  # done
        "degree_type": "学位分类",  # done
        "academic_degree_level": "学位层次",  # done
        "qs_general_program": "QS排名学科分类",
        "qs_program_link": "QS学科网站",
        "university_type": "学校类型",  # done
        "graduation_year": "毕业时间",  # done
        "location": "地理位置",  # done
        "graduation_rate": "毕业率",  #
        "domestic_student_tuition": "本地学生学费",  # done
        "international_student_tuition": "国际学生学费",  # done
        "description": "简介",  # done
        "ranking_qs_subject_2024": "QS专业2024排名",  # done
        "majors_and_employment_direction": "专业及方向",  #
        "university_official_website": "学校官方网站",  #
        "course_requirement": "课程要求",  # done
        "official_enrollment_score_range": "官方录取分数",
        "program_enrollment_number": "项目招收人数",  #
        "enrollment_language_requirement": "录取语言要求",  # done
        "previous_suggested_enrollment_scoreline": "往年建议录取分数线",  #
        "last_year_condition_to_sophomore": "去年大一进入大二条件",
        "career_direction": "就业方向",
        "employment_rate": "就业率",
        "coop_opportunity": "带薪实习机会",
        "statistics": "employment_field_and_salary",
        "case_study": "案例",  #
        "characteristics": "项目特色",
        "others": "其他",  #
    }
    valid_keys = set(en_ch_translation_map.keys())

    def __init__(
        self, program_id: int = -1, university_name: str = None, program_name: str = None, params: Dict[str, str] = None
    ):
        self.program_id: int = program_id
        self.university_name: str = university_name
        self.program_name = program_name
        self.params: Dict[str, str] = params if params is not None else {}

    def to_dict_en(self):
        return {
            "program_id": self.program_id,
            "university_name": self.university_name,
            "program_name": self.program_name,
            **self.params,
        }

    def get_attr(self, attr_name: str, default=None):
        if attr_name not in __class__.valid_keys and attr_name not in self.params:
            raise ValueError(f"Expect a valid attribute name from Program.valid_keys or params, but got '{attr_name}'")
        if hasattr(self, attr_name):
            return getattr(self, attr_name)

        return self.params.get(attr_name, default)

    def update(self, input_dict: Dict[str, str]):
        if "program_id" in input_dict:
            self.program_id = input_dict["program_id"]
        if "university_name" in input_dict:
            self.university_name = input_dict["university_name"]
        if "program_name" in input_dict:
            self.program_name = input_dict["program_name"]
        for key in input_dict:
            if key in self.valid_keys:
                self.params[key] = input_dict[key]

    @staticmethod
    def json_to_program(json_input, language="EN"):
        """Deserialize JSON input into a dictionary using a translation map for keys."""
        if language not in (language_option := ("EN", "CH")):
            raise ValueError(f"University only supports two language: {language_option}, but got {language}")
        data = json.loads(json_input)
        # if language == "CH":
        #     data = .translate(data, University.ch_en_translation_map)
        filtered_data = {
            key: data[key]
            for key in data
            if key in Program.valid_keys and key not in ("id_", "university_name", "program_name")
        }
        return Program(data["program_id"], data["university_name"], data["program_name"], filtered_data)
