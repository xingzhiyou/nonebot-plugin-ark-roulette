import asyncio

from nonebot import get_plugin_config, require

from .ArkSrc import fetch_data_by_name
from .config import Config
from .utils import require_json

_ = require("nonebot_plugin_localstore")

from nonebot_plugin_localstore import get_plugin_data_dir

DATA_DIR = get_plugin_data_dir()

conf = get_plugin_config(Config)
PROXY = conf.proxy

from .schemas import HandbookInfoTable


@require_json(DATA_DIR / "handbook_info_table.json")
def load_handbook(handbook_data: HandbookInfoTable):
    """
    从 handbook_info_table.json 中提取 handbookDict 表下的 storyTitle 和 storyText 数据。
    """

    # 提取 handbookDict 数据
    handbook_dict = handbook_data.get("handbookDict", {})
    formatted_data: dict[str, dict[str, str]] = {}

    for char_id, char_data in handbook_dict.items():
        if "storyTextAudio" in char_data:
            formatted_data[char_id] = {
                story["storyTitle"]: story["stories"][0]["storyText"]
                for story in char_data["storyTextAudio"]
                if "stories" in story and story["stories"]  # noqa: RUF019
            }

    return formatted_data


def retrieve_info(handbook_data: dict[str, dict[str, str]], char_id: str, title: str, info_keyword: str):
    """
    根据角色 ID 和标题提取信息。
    """
    if char_id in handbook_data and title in handbook_data[char_id]:
        gender_info = handbook_data[char_id][title].split("\n")
        for info in gender_info:
            if info_keyword in info:
                return info.split("】")[-1].strip()
    return None


# 示例调用
if __name__ == "__main__":
    _ = asyncio.run(fetch_data_by_name("handbook_info_table", PROXY))
    handbook_stories = load_handbook()
    for char_id, stories in handbook_stories.items():
        gender = retrieve_info(handbook_stories, char_id, "综合体检测试", "物理强度")
        print(f"角色 ID: {char_id}, 值: {gender}")  # noqa: T201  # print in standalone mode
