import json
import os
from concurrent.futures import ThreadPoolExecutor

from .handbook import load_handbook, retrieve_info
from .skin import load_skin_data
from .mapping import load_team_sub_mapping
from .config import Config

confi = Config()  # 实例化配置类

DATA_DIR = confi.data_dir  # 从配置中获取数据目录
character_table_path = os.path.join(DATA_DIR, "character_table.json")
handbook_info_table_path = os.path.join(DATA_DIR, "handbook_info_table.json")
skin_table_path = os.path.join(DATA_DIR, "skin_table.json")

mappings = load_team_sub_mapping(
    os.path.join(DATA_DIR, "uniequip_table.json"),
    os.path.join(DATA_DIR, "handbook_team_table.json"),
)

def load_character_data(data_path):
    """
    从 character_table.json 文件中提取角色数据。
    """
    with open(data_path, "r", encoding="utf-8") as f:
        character_data = json.load(f)

    # 提取角色数据
    formatted_data = {}
    for char_id, char_info in character_data.items():
        formatted_data[char_id] = {
            "name": char_info.get("name"),
            "nationId": char_info.get("nationId"),
            "groupId": char_info.get("groupId"),
            "teamId": char_info.get("teamId"),
            "displayNumber": char_info.get("displayNumber"),
            "appellation": char_info.get("appellation"),
            "profession": char_info.get("profession"),
            "tagList": char_info.get("tagList"),
            "itemObtainApproach": char_info.get("itemObtainApproach"),
            "rarity": char_info.get("rarity"),
            "subProfessionId": char_info.get("subProfessionId"),
            "position": char_info.get("position"),
        }

    return formatted_data


def load_handbook_data(data_path):
    """
    从 handbook_info_table.json 文件中提取 handbookDict 表下的 storyTitle 和 storyText 数据，
    并根据指定的关键字提取信息。
    """
    handbook_stories = load_handbook(data_path)
    formatted_data = {key: {} for key in mappings}

    # 遍历每个角色的故事数据
    for char_id, stories in handbook_stories.items():
        # 提取关键信息
        for key in mappings.keys():
            info = retrieve_info(handbook_stories, char_id, "基础档案", key)
            if info:
                # 使用映射表映射关键词
                mapped_key = mappings.get(key, key)  # 使用映射表映射关键词
                # 确保 mapped_key 存在于 formatted_data 中
                if mapped_key not in formatted_data:
                    formatted_data[mapped_key] = {}
                formatted_data[mapped_key][char_id] = info

    return formatted_data


def merge_data(character_data, handbook_data, skin_data):
    """
    合并角色数据、角色档案和皮肤数据。
    """
    merged_data = {}

    for char_id, char_info in character_data.items():
        # 初始化角色数据
        merged_data[char_id] = {**char_info}

        # 添加 handbook_data 中的关键信息
        for key, data in handbook_data.items():
            if char_id in data:
                merged_data[char_id][key] = data[char_id]

        # 添加 skin_data 中的皮肤信息
        merged_data[char_id]["skins"] = [
            {
                "skinId": skin_info.get("skinId"),
                "modelName": skin_info.get("modelName"),
                "skinGroupName": skin_info.get("skinGroupName"),
                "content": skin_info.get("content"),
                "drawerList": skin_info.get("drawerList"),
                "designerList": skin_info.get("designerList"),
            }
            for skin_id, skin_info in skin_data.items()
            if skin_info.get("charId") == char_id
        ]

    return merged_data


def save_to_json(data, output_path):
    """
    将数据保存到 JSON 文件中。
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def process_data():
    """
    使用多线程加载和处理数据。
    """
    with ThreadPoolExecutor() as executor:
        # 提交任务到线程池
        future_character = executor.submit(load_character_data, character_table_path)
        future_handbook = executor.submit(load_handbook_data, handbook_info_table_path)
        future_skin = executor.submit(load_skin_data, skin_table_path)

        # 获取结果
        character_data = future_character.result()
        handbook_data = future_handbook.result()
        skin_data = future_skin.result()

    # 合并数据
    merged_data = merge_data(character_data, handbook_data, skin_data)
    return merged_data


# 示例调用
if __name__ == "__main__":
    # 使用多线程处理数据
    merged_data = process_data()

    # 保存合并后的数据到 JSON 文件
    save_to_json(merged_data, os.path.join(DATA_DIR, "merged_character_data.json"))
    print("数据合并完成，已保存到 merged_character_data.json 文件中。")
