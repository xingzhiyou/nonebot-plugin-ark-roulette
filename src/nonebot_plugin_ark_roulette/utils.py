import json
import os

from .mapping import load_mappings
    

# 定义数据目录和文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")
uniequip_table_path = os.path.join(DATA_DIR, "uniequip_table.json")
handbook_team_table_path = os.path.join(DATA_DIR, "handbook_team_table.json")
merged_character_data_path = os.path.join(DATA_DIR, "merged_character_data.json")

# 加载映射表
mappings = load_mappings(uniequip_table_path, handbook_team_table_path)

def map_tables(value):
    """
    根据键查询映射表并返回对应的值，支持关键词匹配。
    """

    # 精确匹配
    if value in mappings:
        return mappings[value]
    
    # 关键词匹配
    for key, mapped_value in mappings.items():
        if key in value or value in key:
            return mapped_value
    
    # 如果没有找到匹配的值，则返回原始值
    return value



def search_raw_data(data, keyword):
    """
    在数据中搜索包含关键词的条目。
    """
    results = []
    for key, value in data.items():
        if keyword.lower() in json.dumps(value, ensure_ascii=False).lower():
            results.append({key: value})
    return results


if __name__ == "__main__":
    # 循环运行输入关键词
    with open(merged_character_data_path, "r", encoding="utf-8") as f:
        uniequip_data = json.load(f)
    
    current_data = uniequip_data  # 初始化当前数据为完整数据集

    while True:
        keyword = input("请输入关键词（输入'q'退出，输入'r'重置搜索）：")
        if keyword.lower() == 'q':
            print("退出程序。")
            break
        elif keyword.lower() == 'r':
            current_data = uniequip_data  # 重置当前数据为完整数据集
            print("搜索结果已重置为完整数据集。")
            continue
        
        keyword = map_tables(keyword)  # 使用映射表转换关键词
        results = search_raw_data(current_data, keyword)
        if results:
            print(f"找到 {len(results)} 个包含关键词 '{keyword}' 的条目：")
            for result in results:
                for key, value in result.items():
                    print(f"{key}: {value.get('name', 'N/A')}")
            # 更新当前数据为本次搜索结果
            current_data = {key: value for result in results for key, value in result.items()}
        else:
            print(f"没有找到包含关键词 '{keyword}' 的条目。")


        