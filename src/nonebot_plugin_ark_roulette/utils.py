import os
from .mapping import load_handbook_team_table  # 引入加载函数

from .mapping import (
    load_mappings,
    FIELD_MAPPING,
    PROFESSION_MAPPING,
    POSITION_MAPPING
)


# 定义数据目录和文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")
skin_table_path = os.path.join(DATA_DIR, "skin_table.json")
character_table_path = os.path.join(DATA_DIR, "character_table.json")
uniequip_table_path = os.path.join(DATA_DIR, "uniequip_table.json")
handbook_team_table_path = os.path.join(DATA_DIR, "handbook_team_table.json")
nation_table_path = os.path.join(DATA_DIR, "nation_table.json")

# 加载映射表
SUB_PROFESSION_MAPPING, TEAM_NATION_MAPPING = load_mappings(uniequip_table_path, handbook_team_table_path)

# 加载 handbook_team_table 数据
HANDBOOK_TEAM_MAPPING = load_handbook_team_table(handbook_team_table_path)


def map_value(key, value, is_input=False):
    """
    根据字段类型映射值。
    如果 is_input 为 True，则将中文值映射为英文值（输入映射）。
    如果 is_input 为 False，则将英文值映射为中文值（输出映射）。
    """
    if key == "rarity" and is_input:
        if value.isdigit():  # 如果输入是纯数字
            return f"TIER_{value}"  # 在数字前添加 TIER_ 前缀
        try:
            int(value.split("_")[-1])  # 检查稀有度值是否有效
        except ValueError:
            raise ValueError(f"无效的稀有度值：{value}，请使用数字或有效的稀有度标识（如 TIER_2）。")
    elif key == "profession":
        mapping = PROFESSION_MAPPING
    elif key == "position":
        mapping = POSITION_MAPPING
    elif key == "subProfessionId":
        mapping = SUB_PROFESSION_MAPPING
    elif key in {"teamId", "nationId", "groupId"}:
        mapping = HANDBOOK_TEAM_MAPPING  # 使用 handbook_team_table 的映射
    elif key == "tagList":
        if is_input:
            # 输入映射：将逗号分隔的字符串转换为列表
            return [tag.strip() for tag in value.split(",")]
        else:
            # 输出映射：将列表转换为逗号分隔的字符串
            if isinstance(value, list):  # 确保 value 是列表
                return ", ".join(value)
            else:
                return str(value)  # 如果不是列表，直接转换为字符串
    else:
        # 如果 key 不在已知的映射表中，直接返回原始值
        mapping = {}

    if is_input:
        # 输入映射：中文值 -> 英文值
        return next((k for k, v in mapping.items() if v == value), value) if key != "rarity" else value
    else:
        # 输出映射：英文值 -> 中文值
        return mapping.get(value, value)



