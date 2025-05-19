import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

from nonebot import require

from .handbook import load_handbook, retrieve_info
from .mapping import load_team_sub_mapping
from .schemas import CharacterInfo, FormattedSkinData, MergedMapping
from .skin import load_skin_data as load_skin_data
from .utils import require_json

_ = require("nonebot_plugin_localstore")

from nonebot_plugin_localstore import get_plugin_data_dir

DATA_DIR = get_plugin_data_dir()


@require_json(DATA_DIR / "character_table.json")
def load_character_data(character_data: dict[str, CharacterInfo]):
    """
    从 character_table.json 数据中提取角色数据。
    """

    # 提取角色数据
    formatted_data: dict[str, CharacterInfo] = {}
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


def load_handbook_data():
    """
    从 handbook_info_table.json 文件中提取 handbookDict 表下的 storyTitle 和 storyText 数据，
    并根据指定的关键字提取信息。
    """
    mappings = load_team_sub_mapping()
    handbook_stories = load_handbook()
    formatted_data: dict[str, dict[str, str]] = {key: {} for key in mappings}

    # 遍历每个角色的故事数据
    for char_id, _ in handbook_stories.items():
        # 提取关键信息
        for key in mappings.keys():
            info = retrieve_info(handbook_stories, char_id, "基础档案", key)
            if info:
                # 使用映射表映射关键词
                mapped_key = mappings.get(key, key)  # 使用映射表映射关键词
                # 确保 mapped_key 存在于 formatted_data 中
                formatted_data.setdefault(mapped_key, {})[char_id] = info

    return formatted_data


def merge_data(
    character_data: dict[str, CharacterInfo],
    handbook_data: dict[str, dict[str, str]],
    skin_data: dict[str, FormattedSkinData],
):
    """
    合并角色数据、角色档案和皮肤数据。
    """
    merged_data: dict[str, MergedMapping] = {}

    for char_id, char_info in character_data.items():
        # 初始化角色数据
        merged_data[char_id] = {
            **deepcopy(char_info),
            "skins": [],
            "stories": {
                key: data[char_id] for key, data in handbook_data.items() if char_id in data
            }
        }

        # # 添加 handbook_data 中的关键信息
        # merged_data[char_id]["stories"] = {
        #     key: data[char_id] for key, data in handbook_data.items() if char_id in data
        # }
        # # old implementation
        # for key, data in handbook_data.items():
        #     if char_id in data:
        #         merged_data[char_id][key] = data[char_id]

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
            for _, skin_info in skin_data.items()
            if skin_info.get("charId") == char_id
        ]

    return merged_data


def save_to_json(data: object, output_path: str | Path):
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
        future_character = executor.submit(load_character_data)
        future_handbook = executor.submit(load_handbook_data)
        future_skin = executor.submit(load_skin_data)

        # 获取结果
        character_data = future_character.result()
        handbook_data = future_handbook.result()
        skin_data = future_skin.result()

    # 合并数据
    merged_data = merge_data(character_data, handbook_data, skin_data)
    return merged_data


async def process_data_async():
    character_data, handbook_data, skin_data = await asyncio.gather(
        asyncio.to_thread(load_character_data),
        asyncio.to_thread(load_handbook_data),
        asyncio.to_thread(load_skin_data)
    )

    # 合并数据
    merged_data = merge_data(character_data, handbook_data, skin_data)
    return merged_data


# 示例调用
if __name__ == "__main__":
    # 使用多线程处理数据
    merged_data = process_data()

    # 保存合并后的数据到 JSON 文件
    save_to_json(merged_data, os.path.join(DATA_DIR, "merged_character_data.json"))
    print("数据合并完成，已保存到 merged_character_data.json 文件中。")  # noqa: T201  # print in standalone mode
