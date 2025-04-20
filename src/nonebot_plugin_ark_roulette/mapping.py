import json
from pathlib import Path

FIELD_MAPPING = {
    "name": "姓名",
    "姓名": "name",
    "nationId": "国家",
    "国家": "nationId",
    "groupId": "组织",
    "组织": "groupId",
    "teamId": "团队",
    "团队": "teamId",
    "displayNumber": "编号",
    "编号": "displayNumber",
    "appellation": "称呼",
    "称呼": "appellation",
    "position": "部署方式",
    "部署方式": "position",
    "tagList": "标签",
    "标签": "tagList",
    "rarity": "稀有度",
    "稀有度": "rarity",
    "profession": "职业",
    "职业": "profession",
    "subProfessionId": "子职业",
    "子职业": "subProfessionId",
    "itemObtainApproach": "获取方式",
    "获取方式": "itemObtainApproach",
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
    "先锋": "PIONEER",
    "近卫": "WARRIOR",
    "狙击": "SNIPER",
    "术师": "CASTER",
    "医疗": "MEDIC",
    "辅助": "SUPPORT",
    "重装": "TANK",
    "特种": "SPECIAL",
    "召唤物": "TOKEN",
}

POSITION_MAPPING = {
    "RANGED": "高台",
    "MELEE": "地面",
    "高台": "RANGED",
    "地面": "MELEE",
}

BASIC_ARCHIVES = {
    "性别": "gender",
    "gender": "性别",
    "战斗经验": "combat_experience",
    "combat_experience": "战斗经验",
    "出身地": "birthplace",
    "birthplace": "出身地",
    "制造商": "manufacturer",
    "manufacturer": "制造商",
    "产地": "origin",
    "origin": "产地",
    "生日": "birthday",
    "birthday": "生日",
    "出厂日": "factory_date",
    "factory_date": "出厂日",
    "出厂时间": "factory_time",
    "factory_time": "出厂时间",
    "种族": "race",
    "race": "种族",
    "身高": "height",
    "height": "身高",
    "高度": "altitude",
    "altitude": "高度",
    "重量": "weight",
    "weight": "重量",
    "体重": "body_weight",
    "body_weight": "体重",
    "矿石病感染情况": "oripathy_status",
    "oripathy_status": "矿石病感染情况",
}


RARITY_MAPPING = {
    "1星": "TIER_1",
    "2星": "TIER_2",
    "3星": "TIER_3",
    "4星": "TIER_4",
    "5星": "TIER_5",
    "6星": "TIER_6",
    "一星": "TIER_1",
    "二星": "TIER_2",
    "三星": "TIER_3",
    "四星": "TIER_4",
    "五星": "TIER_5",
    "六星": "TIER_6",
}

def load_sub_profession_mapping(uniequip_table_path):
    """
    加载子职业数据建立双向映射表。
    """
    if not Path(uniequip_table_path).exists():
        return

    with open(uniequip_table_path, "r", encoding="utf-8") as f:
        uniequip_data = json.load(f)

    sub_prof_dict = uniequip_data.get("subProfDict", {})
    mapping = {}
    for key, value in sub_prof_dict.items():
        sub_profession_name = value.get("subProfessionName", key)
        mapping[key] = sub_profession_name  # 正向映射
        mapping[sub_profession_name] = key  # 反向映射

    return mapping

def load_handbook_team_table(handbook_team_table_path):
    """
    加载国家、地区、组织数据建立双向映射表。
    """
    if not Path(handbook_team_table_path).exists():
        return

    with open(handbook_team_table_path, "r", encoding="utf-8") as f:
        handbook_team_data = json.load(f)

    mapping = {}
    for key, value in handbook_team_data.items():
        team_name = value.get("powerName", key)
        mapping[key] = team_name  # 正向映射
        mapping[team_name] = key  # 反向映射

    return mapping


def load_team_sub_mapping(uniequip_table_path, handbook_team_table_path):
    """
    加载子职业和国家、地区、组织数据建立双向映射表。
    """
    sub_profession_mapping = load_sub_profession_mapping(uniequip_table_path) or {}
    team_nation_mapping = load_handbook_team_table(handbook_team_table_path) or {}

    mapping = {
        **sub_profession_mapping,
        **team_nation_mapping,
        **BASIC_ARCHIVES,
        **FIELD_MAPPING
    }

    return mapping

def load_mappings(uniequip_table_path, handbook_team_table_path):
    """
    加载所有映射表并合并为一个大表。
    """
    sub_profession_mapping = load_sub_profession_mapping(uniequip_table_path) or {}
    team_nation_mapping = load_handbook_team_table(handbook_team_table_path) or {}

    # 合并所有映射表
    combined_mapping = {
        **FIELD_MAPPING,
        **PROFESSION_MAPPING,
        **POSITION_MAPPING,
        **RARITY_MAPPING,
        **BASIC_ARCHIVES,
        **sub_profession_mapping,
        **team_nation_mapping,
    }

    return combined_mapping
