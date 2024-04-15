from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import json
from typing import List


example_university = [
    {
        "ID": 5,
        "学校名": "英属哥伦比亚大学",
        "学校类型": "公立 4年",
        "地理位置": "温哥华校区\n奥卡纳干校区",
        "毕业率": None,
        "本地学生学费": "5千加币",
        "平均每年国际学生学费": "4.1万加币",
        "简介": "英属哥伦比亚大学（英语：University of British Columbia，简称UBC），又或译为英属哥伦比亚大学等，简称卑诗大学或卑大，是一所位于加拿大卑诗省的公立大学，也是U15大学联盟、大英国协大学协会、环太平洋大学联盟、和Universitas 21成员之一。截至目前，不列颠哥伦比亚大学共培养了8位诺贝尔奖得主。",
        "排名": "2024 QS News |34\n2023 US News |35\n2024 Times Rank |41\n2023 ARWU Rank |44",
        "学校官方网站": "https://www.ubc.ca/",
        "学校重要日历": "https://calendar.ubc.ca/",
        "统计数据": "本科专业数量: 99\n研究生与博士专业: 84 ",
        "学校专业": "应用科学学院\n建筑与景观建筑学院\n文学院\n听力学与言语科学学院\nSauder商学院\n社区与区域规划学院\n牙科学院\n教育学院\n继续教育学院\n林学院\n研究生与博士后研究院\n新闻学院\n运动学院\n土地与食品系统学院\n法学院，Peter A. Allard法学院\n图书馆、档案与信息研究学院\n医学院\n音乐学院\n护理学院\n药剂科学学院\n人口与公共卫生学院\n公共政策与全球事务学院\n科学学院\n社会工作学院\nUBC Vantage College\n温哥华经济学院",
        "热门专业": "教育专业\n商学院\n工程专业",
        "学校特色": "英属哥伦比亚大学（UBC）以其独特的特色和成就而著称，这些特色和成就共同构成了其作为全球领先的教学、学习和研究中心的声誉。以下是一些关键亮点：\n可持续性领导力：UBC被评为加拿大最可持续发展的大学，展示了其对环境保护和创新可持续实践的承诺。\n丰富的生物多样性：UBC的比提生物多样性博物馆拥有加拿大最大的蓝鲸骨架，为游客提供与世界上最大生物近距离接触的独特体验。\n多元化的校园文化：UBC支持多元文化环境，在两个校园的双语街道标志中体现出来。这些标志结合了英语和Okanagan校区的原住民Nsyilxcen语言，以及温哥华校区的hən̓q̓əmin̓əm̓语言和英语，反映了UBC对当地原住民文化的尊重和融合。",
    },
    {
        "ID": 5,
        "学校名": "UBC",
        "学校类型": "Public University, 4 years ",
        "地理位置": "Vancouver campus\nOkanagan campus",
        "毕业率": None,
        "本地学生学费": "CAD $5399",
        "平均每年国际学生学费": "CAD $41798",
        "简介": "The University of British Columbia (UBC), located in British Columbia, Canada, is a public university and a member of the U15 Group of Canadian Research Universities, the Association of Commonwealth Universities, the Association of Pacific Rim Universities, and Universitas 21. As of now, UBC has produced a total of 8 Nobel Prize laureates.",
        "排名": "2024 QS News |34\n2023 US News |35\n2024 Times Rank |41\n2023 ARWU Rank |44",
        "学校官方网站": "https://www.ubc.ca/",
        "学校重要日历": "https://calendar.ubc.ca/",
        "统计数据": "Undergraduate Programs: 99\nMaster's and PhD Programs: 84",
        "学校专业": "Applied Science, Faculty of\nArchitecture and Landscape Architecture, School of\nArts, Faculty of\nAudiology and Speech Sciences, School of\nBusiness, Sauder School of\nCommunity and Regional Planning, School of\nDentistry, Faculty of\nEducation, Faculty of\nExtended Learning\nForestry, Faculty of\nGraduate and Postdoctoral Studies\nJournalism, School of\nKinesiology, School of\nLand and Food Systems, Faculty of\nLaw, Peter A. Allard School of\nLibrary, Archival and Information Studies, School of\nMedicine, Faculty of\nMusic, School of\nNursing, School of\nPharmaceutical Sciences, Faculty of\nPopulation and Public Health, School of\nPublic Policy and Global Affairs, School of\nScience, Faculty of\nSocial Work, School of\nUBC Vantage College\nVancouver School of Economics",
        "热门专业": "UBC Education Program\nUBC Sauder Business School\nUBC Engineering Program",
        "学校特色": "The University of British Columbia (UBC) is distinguished by a variety of unique features and achievements that contribute to its reputation as a leading global center for teaching, learning, and research. Here are some key highlights:\nSustainability Leadership: UBC has been named the most sustainable university in Canada, showcasing its commitment to environmental stewardship and innovative sustainable practices.\nRich Biodiversity: The Beaty Biodiversity Museum at UBC is home to Canada's largest blue whale skeleton, offering a unique and close encounter with the world's largest creature.\nDiverse Campus Culture: UBC supports a multicultural environment, evident in the bilingual street signs on both campuses. These signs incorporate English and the indigenous Nsyilxcen language at the Okanagan campus and hən̓q̓əmin̓əm̓ language alongside English at the Vancouver campus, reflecting UBC's respect for and integration of local indigenous cultures.",
    },
]

example_program = [
    {
        "ID": 43,
        "专业名": "麦克马斯特健康科学",
        "学校类型": "公立学校，4年",
        "地理位置": "汉密尔顿",
        "毕业率": None,
        "本地学生学费": "6千加币",
        "平均每年国际学生学费": "4.2万加币",
        "简介": "麦克马斯特大学健康科学项目以其在健康、福祉和疾病预防教育与研究方面的创新方法而闻名。该项目提供跨学科体验，融合科学、技术和社会科学，为学生在健康部门的多种职业或进一步的医学院教育做好准备。这个项目的实践学习、问题基础方法和对健康的广泛视角关注，使其成为旨在在医疗保健领域产生重大影响的学生的独特选择。",
        "排名": None,
        "专业及方向": None,
        "学校官方网站": "https://future.mcmaster.ca/programs/health-sciences/",
        "课程要求": "12年级英语 (例: ENG4U, IB ENG HL, AP ENG)\n以下两门其中一门：\n12年级微积分  (例: MCV4U, IB Math HL, AP Calculus AB/BC）\n12年级高等函数 (例: MHF4U, IB Math HL, AP Statistics)\n以下两门其中一门：\n12年级化学 (例: SCH4U, IB Chemistry HL, AP Chemistry)\n12年级生物学 (例: SBI4U, Biology HL, AP Biology)",
        "官方录取分数小": "90+",
        "项目招收人数": 240,
        "录取语言要求": "雅思（IELTS）：总分6.5, 单项不低于6.0\n托福（TOEFL）：总分86, 单项不低于20",
        "往年建议录取分数线": None,
        "去年大一进入大二条件": None,
        "就业方向": None,
        "就业率": None,
        "带薪实习机会": "是",
        "调研数据：就业领域及薪资": None,
        "案例": "学生高中体系 : 安省           \n录取分数range ： 90+     \n学生课外活动情况 ：100+小时义工      \n奖学金情况 ：\n选课：SBI4U, SCH4U, SPH4U, MHF4U, MCV4U     \n学术类背景提升：AP物理化学生物考试， CCC竞赛前3%\n领导力背景提升 ：医院实习  ",
        "项目特色": "生命科学研究：在生物医学、生态学和分子生物学等领域进行深入研究。\n跨学科学习：鼓励学生跨学科学习，解决复杂的生命科学问题。\n实验室和实践经验：提供先进的实验室设施和丰富的实践经验。\n行业合作：与医疗卫生和生物技术行业有紧密的合作关系，为学生的职业发展铺路。",
        "其他": None,
    },
    {
        "ID": 43,
        "专业名": "McMaster Health Sciences",
        "学校类型": "Public University, 4 years",
        "地理位置": "Hamilton",
        "毕业率": None,
        "本地学生学费": "CAD $6042",
        "平均每年国际学生学费": "CAD $45271",
        "简介": "The McMaster University Health Sciences program is renowned for its innovative approach to education and research in health, wellness, and disease prevention. It offers an interdisciplinary experience, blending science, technology, and social sciences, to prepare students for a variety of careers in the health sector or further education in medical school. This program's hands-on learning, problem-based approach, and focus on health from a broad perspective make it a unique choice for students aiming to make a significant impact in healthcare.",
        "排名": None,
        "专业及方向": None,
        "学校官方网站": "https://future.mcmaster.ca/programs/health-sciences/",
        "课程要求": "Grade 12 level English (ex.ENG4U, IB ENG HL, AP ENG)\n1 of the following:\nGrade 12 level Calculus (ex.MCV4U, IB Math HL, AP Calculus AB/BC)\nGrade 12 level Functions (ex.MHF4U, IB Math HL, AP Statistics)\n1 of the following:\nGrade 12 level Chemistry (ex.SCH4U, IB Chemistry HL, AP Chemistry)\nGrade 12 level Biology (ex. SBI4U, Biology HL, AP Biology)",
        "官方录取分数小": "90+",
        "项目招收人数": 240,
        "录取语言要求": "IELTS: 6.5 overall, with no part less than 6.0\nTOFEL:86 overall, with no part less than 20",
        "往年建议录取分数线": None,
        "去年大一进入大二条件": None,
        "就业方向": None,
        "就业率": None,
        "带薪实习机会": "Yes",
        "调研数据：就业领域及薪资": None,
        "案例": "Student's high school system: Ontario\nAdmission score range: 90+ \nExtracurricular activities: 100+ hours of volunteering\nScholarship:\nCourse selection: SBI4U, SCH4U, SPH4U, MHF4U, MCV4U\nAcademic background enhancement: AP Physics，Biology and Chemistry, CCC Contest top 3%\nLeadership background enhancement: Hospital Co-op",
        "项目特色": "Life Sciences Research: Conducts in-depth research in areas such as biomedical sciences, ecology, and molecular biology.\nInterdisciplinary Learning: Encourages interdisciplinary learning to address complex life sciences challenges.\nLaboratory and Practical Experience: Offers advanced laboratory facilities and extensive practical experience.\nIndustry Collaboration: Has close collaborations with the healthcare and biotechnology industries, paving the way for students' career development.",
        "其他": None,
    },
]


def get_sheet_client(credential_json_file: str = "uforseAdminKey.json"):
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    # local contains uforseAdminKey.json
    creds = ServiceAccountCredentials.from_json_keyfile_name(credential_json_file, scope)
    return gspread.authorize(creds)


# Function to check and recreate the sheet if it exists
def recreate_sheet(sheet_client: gspread.Client, title: str, spreadsheet_title="working_extract_info_output"):
    sheet = sheet_client.open(spreadsheet_title)
    # Check if "title" sheet exists and delete it
    worksheet_list = sheet.worksheets()
    for worksheet in worksheet_list:
        if worksheet.title == title:
            sheet.del_worksheet(worksheet)
            print(f"Worksheet '{title}' found and deleted.")
            break
    sheet.add_worksheet(title=title, rows="100", cols="20")
    print(f"New '{title}' worksheet created.")
    return sheet.worksheet(title)


def insert_new_rows(
    sheet_client: gspread.Client, cache_column_name: str, cache, spreadsheet_title: str = "working_extract_info_output"
):
    new_sheet = recreate_sheet(sheet_client, cache_column_name, spreadsheet_title)
    headers = cache[cache_column_name][0].keys()
    rows = [list(item.values()) for item in cache[cache_column_name]]  # Convert dict values to list
    # Insert headers and rows into the new worksheet
    new_sheet.append_row(list(headers))  # Insert headers
    for row in rows:
        new_sheet.append_row(row)  # Insert each row
    print(f"Data added to '{cache_column_name}' worksheet successfully.")


def load_cache(cache_path):
    with open(cache_path, "r", encoding="utf-8") as cache_file:
        cache = json.load(cache_file)
    return cache


def store_cache(cache_path, cache):
    with open(cache_path, "w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file)


def get_example(action: str, sheet_client: gspread.Client):
    cache_repo_path = "./cache_repo"
    if action == "load_from_cache":
        try:
            cache = load_cache(os.path.join(cache_repo_path, "example_cache.json"))
            print("Cache loaded successfully.")
            for key in cache:
                insert_new_rows(sheet_client, key, cache)
        except FileNotFoundError:
            print("Cache file not found. Starting with an empty cache.")
            cache = {}
        return cache
    if action == "save_to_cache":
        cache = {"example_university": example_university, "example_program": example_program}
        store_cache(os.path.join(cache_repo_path, "example_cache.json"), cache)
        return cache
    return {}


def get_expect_column(
    sheet_client: gspread.Client = get_sheet_client(),
    spreadsheet_title: str = "working_extract_info_output",
    sheet_title: str = "example_university",
):
    return sheet_client.open(spreadsheet_title).worksheet(sheet_title).row_values(1)


def restore_by_cache(cache_file_path, sheet_client: gspread.Client):
    try:
        with open(cache_file_path, "r", encoding="utf-8") as cache_file:
            cache = json.load(cache_file)
        print("Cache loaded successfully.")
        for key in cache:
            insert_new_rows(sheet_client, key, cache)
    except FileNotFoundError:
        print("Cache file not found. Starting with an empty cache.")
        cache = {}


def get_worksheet(sheetname: str, sheet_client: gspread.Client = get_sheet_client()):
    return sheet_client.open("working_extract_info_output").worksheet(sheetname)


def get_worksheet_records(sheet_title: str, sheet_client: gspread.Client = get_sheet_client()):
    worksheet = get_worksheet(sheet_title, sheet_client)
    # Fetch all records from the sheet to a list of dictionaries
    records = worksheet.get_all_records()

    # Serialize the list of dictionaries to a JSON string
    return {sheet_title: records}


def get_expect_column(
    sheet_client: gspread.Client = get_sheet_client(),
    spreadsheet_title: str = "working_extract_info_output",
    sheet_title: str = "example_university",
):
    return sheet_client.open(spreadsheet_title).worksheet(sheet_title).row_values(1)



if __name__ == "__main__":
    cache_repo_path = "./cache_repo"
    restore_by_cache(os.path.join(cache_repo_path, "target_university_before_action.json"), get_sheet_client())
