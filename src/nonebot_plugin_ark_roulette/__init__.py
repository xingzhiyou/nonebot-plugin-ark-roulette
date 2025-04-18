import os
import random
from nonebot.plugin import PluginMetadata
from nonebot import on_command, logger, get_driver
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg

from .fetch_data import fetch_and_save_data, find_matching_characters, get_drawer_list_from_skin_table
from .mapping import (
    load_mappings,
    FIELD_MAPPING,
    PROFESSION_MAPPING,
    POSITION_MAPPING
)
from .utils import map_value

__plugin_meta__ = PluginMetadata(
    name="明日方舟干员插件",
    description="提供明日方舟干员筛选与随机选择功能的插件。",
    usage="使用 /筛选 或 /随机选择 命令来获取干员信息。",
    type="application",
    homepage="https://github.com/xingzhiyou/nonebot-plugin-ark-roulette",
)

# 定义数据目录和文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")
skin_table_path = os.path.join(DATA_DIR, "skin_table.json")
character_table_path = os.path.join(DATA_DIR, "character_table.json")
uniequip_table_path = os.path.join(DATA_DIR, "uniequip_table.json")
handbook_team_table_path = os.path.join(DATA_DIR, "handbook_team_table.json")
nation_table_path = os.path.join(DATA_DIR, "nation_table.json")



find_operator = on_command("筛选", aliases={"筛选干员"}, priority=5, block=True)
random_operator = on_command("随机选择", aliases={"随机干员"}, priority=5, block=True)
update_data = on_command("更新数据", aliases={"更新干员数据"}, priority=5, block=True, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@update_data.handle()
async def handle_update_data(bot: Bot, event: MessageEvent):
    """
    处理更新数据命令。
    """
    try:
        await update_data.send("正在更新干员数据，请稍等...")
        fetch_and_save_data(DATA_DIR)
        await update_data.send("干员数据更新完成！")
    except FinishedException:
        pass
    except Exception as e:
        logger.error(f"更新数据时发生错误：{e}")
        await update_data.send("更新数据失败，请检查日志。")


@find_operator.handle()
async def handle_find_operator(event: MessageEvent):
    """
    处理筛选干员命令。
    """
    try:
        # 获取用户输入的筛选条件
        user_input = event.message.extract_plain_text().strip()
        if user_input == "筛选" or user_input == "筛选干员":
            await find_operator.send("请输入筛选条件，例如：/筛选 稀有度=5 职业=狙击 标签=输出,生存 子职业=强化")
            return

        # 去除命令前缀
        if user_input.startswith("筛选"):
            user_input = user_input[len("筛选"):].strip()

        # 解析用户输入的筛选条件
        search_criteria = {}
        for condition in user_input.split():
            if "=" in condition:
                key, value = condition.split("=", 1)
                key = key.strip()
                value = value.strip()

                # 将中文键转换为英文键
                english_key = next((k for k, v in FIELD_MAPPING.items() if v == key), key)

                try:
                    # 使用 map_value 处理输入映射
                    value = map_value(english_key, value, is_input=True)
                except ValueError as e:
                    await find_operator.send(str(e))
                    return

                search_criteria[english_key] = value
            else:
                await find_operator.send(f"无效的筛选条件：{condition}，请使用 key=value 格式。")
                return

        logger.info(f"筛选条件：{search_criteria}")

        # 获取符合条件的角色
        matching_characters = find_matching_characters(
            character_table_path=character_table_path,
            search_criteria=search_criteria
        )

        if not matching_characters:
            await find_operator.send("没有找到符合条件的干员。")
            return

        # 格式化输出结果，添加职业、部署方式、子职业、团队和国家映射
        result = "\n\n".join(
            "\n".join(
                f"{FIELD_MAPPING.get(key, key)}: {map_value(key, char.get(key, '未知'))}"
                for key in FIELD_MAPPING.keys() if key in char
            )
            for char in matching_characters
        )
        await find_operator.send(f"符合条件的干员有：\n{result}")

    except FinishedException:
        pass
    except Exception as e:
        logger.error(f"筛选干员时发生错误：{e}")
        await find_operator.send("筛选干员失败，请检查日志。")

