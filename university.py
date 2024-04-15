import json
from typing import List, Dict, Union
from pprint import pprint


def str_to_list(arg: Union[str, List[str]], splitter=None) -> List[str]:
    """
    Converts a single string into a list of substrings, or returns the list unchanged if the input is already a list.
    """
    if not isinstance(arg, str):
        return arg
    return list(arg.split(splitter)) if splitter else list(arg.split())


class University:
        """
    A class representing details about a university, encapsulating various attributes related to university information.

    Attributes:
        id (int): Unique identifier for the university, default is 0.
        university_name (str): The full name of the university.
        abbreviation (str): The common abbreviation of the university's name.
        university_type (str): The type of university (e.g., public, private).
        graduation_year (float): Year of graduation.
        location (List[str]): The geographical location(s) of the university.
        graduation_rate (float): The graduation rate of the university.
        domestic_student_tuition (float): Tuition fees for domestic students.
        international_student_tuition (float): Tuition fees for international students.
        description (str): A brief description of the university.
        ranking (List[str]): Rankings of the university across various platforms or criteria.
        website (str): Official website of the university.
        important_calendar (str): Key dates and events in the university's academic calendar.
        statistics (List[str]): List of important statistics about the university.
        faculty (List[str]): List of faculties or departments within the university.
        popular_programs (List[str]): List of popular academic programs offered by the university.
        characteristics (List[str]): Distinctive features or characteristics of the university.
        wikipedia (str): Wikipedia link for the university.
        others (str): Additional information about the university.

    Methods:
        __init__: Initializes the University object with the provided values for its attributes.
        __repr__: Provides a simple string representation of the university.
        to_dict_ch: Returns a dictionary representation of the university's attributes with keys in Chinese.
        to_dict_en: Returns a dictionary representation of the university's attributes with keys in English.

    Example:
        >>> university = University(
                university_name="University of Waterloo",
                id=1,
                abbreviation="UW",
                university_type="Public",
                graduation_year=2024,
                location=["Waterloo, Ontario, Canada"],
                graduation_rate=88.5,
                domestic_student_tuition=8000,
                international_student_tuition=32000,
                description="Known for its cooperative education programs.",
                ranking=["Top 100 Worldwide"],
                website="https://www.uwaterloo.ca",
                important_calendar="Fall Semester starts in September",
                statistics=["Enrollment: 35000"],
                faculty=["Engineering", "Mathematics", "Science"],
                popular_programs=["Computer Science", "Mechanical Engineering"],
                characteristics=["Innovative", "Entrepreneurial"],
                wikipedia="https://en.wikipedia.org/wiki/University_of_Waterloo"
            )
        >>> print(university)
        University(ID=1, Name=University of Waterloo)
    """
    def __init__(
        self,
        university_name: str,
        id: int = 0,
        abbreviation: str = "",
        university_type: str = "",
        graduation_year: float = 0.0,
        location: List[str] = None,
        graduation_rate: float = 0.0,
        domestic_student_tuition: float = 0.0,
        international_student_tuition: float = 0.0,
        description: str = "",
        ranking: List[str] = None,
        website: str = "",
        important_calendar: str = "",
        statistics: List[str] = None,
        faculty: List[str] = None,
        popular_programs: List[str] = None,
        characteristics: List[str] = None,
        wikipedia: str = "",
        others: str = "",
    ):
        self.id = id
        self.university_name = university_name
        self.abbreviation = abbreviation
        self.university_type = university_type
        self.graduation_year = graduation_year
        if isinstance(location, str):
            location = list(location.split())
        self.location = str_to_list(location) if location is not None else []
        self.graduation_rate = graduation_rate
        self.domestic_student_tuition = domestic_student_tuition
        self.international_student_tuition = international_student_tuition
        self.description = description
        self.ranking = str_to_list(ranking, "\n") if ranking is not None else []
        self.website = website
        self.important_calendar = important_calendar
        self.statistics = str_to_list(statistics, "\n") if statistics is not None else []
        self.faculty = str_to_list(faculty, "\n") if faculty is not None else []
        self.popular_programs = str_to_list(popular_programs, "\n") if popular_programs is not None else []
        self.characteristics = str_to_list(characteristics, "\n") if characteristics is not None else []
        self.wikipedia = wikipedia
        self.others = others

    def __repr__(self):
        return f"University(ID={self.id}, Name={self.university_name})"

    def to_dict_ch(self):
        # Convert None to 'null' for JSON compatibility
        return {
            "ID": self.id,
            "学校名": self.university_name,
            "缩写": self.abbreviation,
            "学校类型": self.university_type,
            "毕业时间": self.graduation_year,
            "地理位置": self.location,
            "毕业率": self.graduation_rate,
            "本地学生学费": self.domestic_student_tuition,
            "国际学生学费": self.international_student_tuition,
            "简介": self.description,
            "排名": self.ranking,
            "学校官方网站": self.website,
            "学校重要日历": self.important_calendar,
            "统计数据": self.statistics,
            "院校": self.faculty,
            "热门专业": self.popular_programs,
            "学校特色": self.characteristics,
            "其他": self.others,
        }

    def to_dict_en(self):
        # Convert None to 'null' for JSON compatibility
        return self.__dict__


def json_to_university_en(json_input: json):
    # Parse the JSON string into a Python dictionary
    data: Dict = json.loads(json_input)

    # Initialize a University object with the data
    university = University(
        university_name=data.get("university_name", ""),
        id=data.get("id", 0),
        abbreviation=data.get("abbreviation", ""),
        university_type=data.get("university_type", ""),
        graduation_year=data.get("graduation_year", 0.0),
        location=data.get("location", []),
        graduation_rate=data.get("graduation_rate", 0.0),
        domestic_student_tuition=data.get("domestic_student_tuition", 0.0),
        international_student_tuition=data.get("international_student_tuition", 0.0),
        description=data.get("description", ""),
        ranking=data.get("ranking", []),
        website=data.get("website", ""),
        important_calendar=data.get("important_calendar", ""),
        statistics=data.get("statistics", []),
        faculty=data.get("faculty", []),
        popular_programs=data.get("popular_programs", []),
        characteristics=data.get("features", []),
        wikipedia=data.get("wikipedia", ""),
        others=data.get("others", "")
    )

    return university


def json_to_university_ch(json_input):
    # Parse the JSON string into a Python dictionary
    data: Dict = json.loads(json_input)

    # Initialize a University object using the Chinese keys from the JSON data
    university = University(
        university_name=data.get("学校名", ""),
        id=data.get("ID", 0),
        abbreviation=data.get("缩写", ""),
        university_type=(
            data.get("学校类型", "")
        ),
        graduation_year=(
            data.get("毕业年数", 4)
        ),
        location=data.get("地理位置", []),
        graduation_rate=data.get("毕业率", 0.0),
        domestic_student_tuition=data.get("本地学生学费", 0.0),
        international_student_tuition=data.get("国际学生学费", 0.0),
        description=data.get("简介", ""),
        ranking=data.get("排名", []),
        website=data.get("学校官方网站", ""),
        important_calendar=data.get("学校重要日历", ""),
        statistics=data.get("统计数据", []),
        faculty=data.get("院校", []),
        popular_programs=data.get("热门专业", []),
        characteristics=data.get("学校特色", []),
        wikipedia=data.get("维基百科页", "")
    )
    return university


if __name__ == "__main__":
    ubc = University(
        id=5,
        university_name="英属哥伦比亚大学",
        university_type="公立",
        graduation_year=4,
        location="温哥华校区\n奥卡纳干校区",
        graduation_rate=None,
        domestic_student_tuition=5000,
        international_student_tuition=41000,
        description="英属哥伦比亚大学（英语：University of British Columbia，简称UBC），又或译为英属哥伦比亚大学等，简称卑诗大学或卑大，是一所位于加拿大卑诗省的公立大学，也是U15大学联盟、大英国协大学协会、环太平洋大学联盟、和Universitas 21成员之一。截至目前，不列颠哥伦比亚大学共培养了8位诺贝尔奖得主。",
        ranking="2024 QS News |34\n2023 US News |35\n2024 Times Rank |41\n2023 ARWU Rank |44",
        website="https://www.ubc.ca/",
        important_calendar="https://calendar.ubc.ca/",
        statistics="本科专业数量: 99\n研究生与博士专业: 84",
        faculty="应用科学学院\n建筑与景观建筑学院\n文学院\n听力学与言语科学学院\nSauder商学院\n社区与区域规划学院\n牙科学院\n教育学院\n继续教育学院\n林学院\n研究生与博士后研究院\n新闻学院\n运动学院\n土地与食品系统学院\n法学院，Peter A. Allard法学院\n图书馆、档案与信息研究学院\n医学院\n音乐学院\n护理学院\n药剂科学学院\n人口与公共卫生学院\n公共政策与全球事务学院\n科学学院\n社会工作学院\nUBC Vantage College\n温哥华经济学院",
        popular_programs="教育专业\n商学院\n工程专业",
        characteristics="英属哥伦比亚大学（UBC）以其独特的特色和成就而著称，这些特色和成就共同构成了其作为全球领先的教学、学习和研究中心的声誉。以下是一些关键亮点：\n可持续性领导力：UBC被评为加拿大最可持续发展的大学，展示了其对环境保护和创新可持续实践的承诺。\n丰富的生物多样性：UBC的比提生物多样性博物馆拥有加拿大最大的蓝鲸骨架，为游客提供与世界上最大生物近距离接触的独特体验。\n多元化的校园文化：UBC支持多元文化环境，在两个校园的双语街道标志中体现出来。这些标志结合了英语和Okanagan校区的原住民Nsyilxcen语言，以及温哥华校区的hən̓q̓əmin̓əm̓语言和英语，反映了UBC对当地原住民文化的尊重和融合。",
        wikipedia="https://en.wikipedia.org/wiki/University_of_British_Columbia"
    )
    pprint(ubc.to_dict_en())
