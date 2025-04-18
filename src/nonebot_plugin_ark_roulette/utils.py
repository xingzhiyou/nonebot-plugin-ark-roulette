import json
import os

from .mapping import (
    load_mappings,
    PROFESSION_MAPPING,
    POSITION_MAPPING
)
    

# 定义数据目录和文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")
uniequip_table_path = os.path.join(DATA_DIR, "uniequip_table.json")
handbook_team_table_path = os.path.join(DATA_DIR, "handbook_team_table.json")

# 加载映射表
SUB_PROFESSION_MAPPING, TEAM_NATION_MAPPING = load_mappings(uniequip_table_path, handbook_team_table_path)

def map_tables(value):
    """
    根据键查询映射表并返回对应的值，支持关键词匹配。
    """
    # 将四个表的映射表合并
    combined_mapping = {**PROFESSION_MAPPING, **POSITION_MAPPING, **SUB_PROFESSION_MAPPING, **TEAM_NATION_MAPPING}
    
    # 精确匹配
    if value in combined_mapping:
        return combined_mapping[value]
    
    # 关键词匹配
    for key, mapped_value in combined_mapping.items():
        if key in value or value in key:
            return mapped_value
    
    # 如果没有找到匹配的值，则返回原始值
    return value



if __name__ == "__main__":
    # 测试映射函数
    test_values = ["先锋", "先锋干员", "地面", "melee", "岁", "TOKEN"]
    for value in test_values:
        mapped_value = map_tables(value)
        print(f"原始值: {value} -> 映射值: {mapped_value}")