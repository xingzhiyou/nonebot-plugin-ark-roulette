import json
from pathlib import Path

FIELD_MAPPING = {
    "name": "姓名",
    "nationId": "国家",
    "groupId": "组织",
    "teamId": "团队",
    "displayNumber": "编号",
    "appellation": "称呼",
    "position": "部署方式",
    "tagList": "标签",
    "rarity": "稀有度",
    "profession": "职业",
    "subProfessionId": "子职业"
}

PROFESSION_MAPPING = {
    "PIONEER": "先锋",
    "WARRIOR": "近卫",
    "SNIPER": "狙击",
    "CASTER": "术师",
    "MEDIC": "医疗",
    "SUPPORT": "辅助",
    "TANK": "重装",
    "SPECIAL": "特种",
    "TOKEN": "召唤物",
}

POSITION_MAPPING = {
    "RANGED": "高台",
    "MELEE": "地面",
}

def load_sub_profession_mapping(json_file_path):
    """
    从 JSON 文件加载子职业映射表。
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    sub_profession_mapping = {}
    sub_prof_dict = data.get("subProfDict", {})
    for sub_prof_id, details in sub_prof_dict.items():
        sub_profession_mapping[sub_prof_id] = details.get("subProfessionName", sub_prof_id)
    
    return sub_profession_mapping

def load_handbook_team_table(handbook_team_table_path):
    """
    加载 handbook_team_table.json 并生成映射表。
    """
    with open(handbook_team_table_path, "r", encoding="utf-8") as f:
        handbook_data = json.load(f)

    mapping = {}
    for key, value in handbook_data.items():
        mapping[key] = value.get("powerName", key)  # 使用 powerName 作为中文映射
        mapping[value.get("powerName", key)] = key  # 反向映射

    return mapping


def load_mappings(uniequip_table_path, handbook_team_table_path):
    """
    加载所有映射表。
    """
    sub_profession_mapping = load_sub_profession_mapping(uniequip_table_path)
    team_nation_mapping = load_handbook_team_table(handbook_team_table_path)
    return sub_profession_mapping, team_nation_mapping

