import json
from collections.abc import Hashable, Mapping
from typing import TypeVar

from nonebot import require

_ = require("nonebot_plugin_localstore")

from nonebot_plugin_localstore import get_plugin_data_dir

DATA_DIR = get_plugin_data_dir()

from .schemas import HandbookTeam, UniEquipTable
from .utils import require_json

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


@require_json(DATA_DIR / "uniequip_table.json")
def load_sub_profession_mapping(uniequip_data: UniEquipTable):
    """
    加载子职业数据建立双向映射表。
    """

    sub_prof_dict = uniequip_data.get("subProfDict", {})
    mapping: dict[str, str] = {}
    for key, value in sub_prof_dict.items():
        sub_profession_name = value.get("subProfessionName", key)
        mapping[key] = sub_profession_name  # 正向映射
        mapping[sub_profession_name] = key  # 反向映射

    return mapping


@require_json(DATA_DIR / "handbook_team_table.json")
def load_handbook_team_table(handbook_team_data: dict[str, HandbookTeam]):
    """
    加载国家、地区、组织数据建立双向映射表。
    """

    mapping: dict[str, str] = {}
    for key, value in handbook_team_data.items():
        team_name = value.get("powerName", key)
        mapping[key] = team_name  # 正向映射
        mapping[team_name] = key  # 反向映射

    return mapping


def load_team_sub_mapping():
    """
    加载子职业和国家、地区、组织数据建立双向映射表。
    """
    sub_profession_mapping = load_sub_profession_mapping() or {}
    team_nation_mapping = load_handbook_team_table() or {}

    mapping = {**sub_profession_mapping, **team_nation_mapping, **BASIC_ARCHIVES, **FIELD_MAPPING}

    return mapping


def load_mappings():
    """
    加载所有映射表并合并为一个大表。
    """
    sub_profession_mapping = load_sub_profession_mapping() or {}
    team_nation_mapping = load_handbook_team_table() or {}

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


def map_tables(value: str):
    """
    根据键查询映射表并返回对应的值，支持关键词匹配。
    """
    # 加载映射表
    mappings = load_mappings()

    # 精确匹配
    if value in mappings:
        return mappings[value]

    # 关键词匹配
    for key, mapped_value in mappings.items():
        if key in value or value in key:
            return mapped_value

    # 如果没有找到匹配的值，则返回原始值
    return value


KT = TypeVar("KT", bound=Hashable)
VT = TypeVar("VT")


def search_raw_data(data: Mapping[KT, VT], keyword: str) -> list[Mapping[KT, VT]]:
    """
    在数据中搜索包含关键词的条目。
    """
    results: list[Mapping[KT, VT]] = []
    for key, value in data.items():
        if keyword.lower() in json.dumps(value, ensure_ascii=False).lower():
            results.append({key: value})
    return results


if __name__ == "__main__":
    # 循环运行输入关键词
    with open(DATA_DIR / "merged_character_data.json", encoding="utf-8") as f:
        uniequip_data = json.load(f)

    current_data = uniequip_data  # 初始化当前数据为完整数据集

    while True:
        keyword = input("请输入关键词（输入'q'退出，输入'r'重置搜索）：")
        if keyword.lower() == "q":
            print("退出程序。")  # noqa: T201  # print in standalone mode
            break
        elif keyword.lower() == "r":
            current_data = uniequip_data  # 重置当前数据为完整数据集
            print("搜索结果已重置为完整数据集。")  # noqa: T201
            continue

        keyword = map_tables(keyword)  # 使用映射表转换关键词
        results = search_raw_data(current_data, keyword)
        if results:
            print(f"找到 {len(results)} 个包含关键词 '{keyword}' 的条目：")  # noqa: T201
            for result in results:
                for key, value in result.items():
                    print(f"{key}: {value.get('name', 'N/A')}")  # noqa: T201
            # 更新当前数据为本次搜索结果
            current_data = {key: value for result in results for key, value in result.items()}
        else:
            print(f"没有找到包含关键词 '{keyword}' 的条目。")  # noqa: T201
