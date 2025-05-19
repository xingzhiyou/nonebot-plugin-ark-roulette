# pyright: reportUnknownMemberType=none

import asyncio
import json
import os
from typing import Any

from nonebot import get_driver, logger, on_command, require
from nonebot.adapters import Event, Message

# from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata, get_plugin_config

_ = require("nonebot_plugin_localstore")

from nonebot_plugin_localstore import get_plugin_data_dir

DATA_DIR = get_plugin_data_dir()

from .ArkSrc import check_resource_exists, fetch_and_save_data_async
from .config import Config
from .mapping import map_tables, search_raw_data
from .saveData import load_character_data, load_handbook_data, load_skin_data, merge_data, save_to_json
from .schemas import MergedMapping

__plugin_meta__ = PluginMetadata(
    name="明日方舟干员插件",
    description="提供明日方舟干员筛选与随机选择功能的插件。",
    usage="使用 /筛选 或 /随机选择 命令来获取干员信息。",
    type="application",
    homepage="https://github.com/xingzhiyou/nonebot-plugin-ark-roulette",
    config=Config,
    supported_adapters=None,
)

conf = get_plugin_config(Config)
driver = get_driver()

skin_table_path = DATA_DIR / "skin_table.json"
character_table_path = DATA_DIR / "character_table.json"
handbook_info_table_path = DATA_DIR / "handbook_info_table.json"
merged_character_data_path = DATA_DIR / "merged_character_data.json"

find_operator = on_command("筛选", aliases={"筛选干员"}, priority=5, block=True)
random_operator = on_command("随机选择", aliases={"随机干员", "roll"}, priority=5, block=True)
update_data = on_command("更新数据", aliases={"更新干员数据"}, priority=5, block=True, permission=SUPERUSER)

find_operator_sessions: dict[str, dict[str, MergedMapping]] = {}
find_operator_histories: dict[str, list[dict[str, MergedMapping]]] = {}
SESSION_TIMEOUT = 120
session_timeout_tasks = {}


def reset_session_timeout(user_id: str):
    if user_id in session_timeout_tasks:
        session_timeout_tasks[user_id].cancel()

    async def session_timeout():
        try:
            await asyncio.sleep(SESSION_TIMEOUT)
            logger.info(f"用户 {user_id} 的筛选会话超时，自动退出筛选模式。")
            _ = find_operator_sessions.pop(user_id, None)
            _ = find_operator_histories.pop(user_id, None)
            session_timeout_tasks.pop(user_id, None)
            await find_operator.finish("由于长时间未操作，已自动退出筛选模式。")
        except FinishedException:
            pass

    session_timeout_tasks[user_id] = asyncio.create_task(session_timeout())


@driver.on_startup
async def auto_update_data():
    try:
        if not conf.update_on_launch or (check_resource_exists() and merged_character_data_path.is_file()):
            logger.info("干员数据已存在，跳过自动下载数据。如有需要请使用命令触发。")
            return
        logger.info("开始更新干员数据...")
        _ = await fetch_and_save_data_async()
        merged_data = merge_data(
            load_character_data(),
            load_handbook_data(),
            load_skin_data(),
        )
        save_to_json(merged_data, merged_character_data_path)
        logger.info("干员数据更新完成！")
    except Exception:
        logger.exception("更新数据时发生错误：")


@update_data.handle()
async def handle_update_data():
    try:
        logger.info("开始更新干员数据...")
        await update_data.send("正在更新干员数据，请稍等...")
        _ = await fetch_and_save_data_async()
        merged_data = merge_data(
            load_character_data(),
            load_handbook_data(),
            load_skin_data(),
        )
        save_to_json(merged_data, merged_character_data_path)
        logger.info("干员数据更新完成！")
        await update_data.send("干员数据更新完成！")
    except Exception:
        logger.exception("更新数据时发生错误：")
        await update_data.send("更新数据失败，请检查日志。")


@find_operator.handle()
async def handle_find_operator(event: Event, args: Message[Any] = CommandArg()):
    user_id = event.get_user_id()

    if not os.path.exists(merged_character_data_path):
        await find_operator.finish("资源文件不存在，请使用 /更新数据 命令获取最新的干员数据后再尝试。")

    if user_id not in find_operator_sessions:
        with open(merged_character_data_path, encoding="utf-8") as f:  # noqa: ASYNC230
            find_operator_sessions[user_id] = json.load(f)
        find_operator_histories[user_id] = []

    current_data = find_operator_sessions[user_id]
    keywords = args.extract_plain_text().strip()

    if not keywords:
        await find_operator.finish(
            "【筛选干员命令说明】\n"
            "使用方法：\n"
            "/筛选 <关键词1> <关键词2> ...\n"
            "支持的功能：\n"
            "1. 输入多个关键词用空格分隔，例如：/筛选 六星 狙击 男\n"
            "2. 输入 'r' 重置筛选结果。\n"
            "3. 输入 'd' 撤销上一个关键词筛选。\n"
            "4. 输入 'q' 退出筛选模式。\n"
            "如果 120 秒内没有操作，系统将自动退出筛选模式。"
        )

    reset_session_timeout(user_id)

    if keywords.lower() == "q":
        _ = find_operator_sessions.pop(user_id, None)
        _ = find_operator_histories.pop(user_id, None)
        session_timeout_tasks.pop(user_id, None).cancel()
        await find_operator.finish("已退出筛选模式。")
    elif keywords.lower() == "r":
        with open(merged_character_data_path, encoding="utf-8") as f:  # noqa: ASYNC230
            find_operator_sessions[user_id] = json.load(f)
        find_operator_histories[user_id] = []
        await find_operator.finish("搜索结果已重置为完整数据集。")
    elif keywords.lower() == "d":
        if find_operator_histories[user_id]:
            find_operator_sessions[user_id] = find_operator_histories[user_id].pop()
            await find_operator.finish("已撤销上一个关键词筛选。")
        else:
            await find_operator.finish("没有可以撤销的筛选操作。")

    keyword_list = keywords.split()
    find_operator_histories[user_id].append(current_data.copy())

    for keyword in keyword_list:
        keyword = map_tables(keyword)
        results = search_raw_data(current_data, keyword)
        if results:
            current_data = {key: value for result in results for key, value in result.items()}
        else:
            await find_operator.finish(f"没有找到包含关键词 '{' '.join(keyword_list)}' 的条目。")

    find_operator_sessions[user_id] = current_data
    names: list[str] = [value.get("name", "N/A") for _, value in current_data.items()]
    result_text = (
        f"找到 {len(current_data)} 个包含关键词 '{' '.join(keyword_list)}' 的条目：\n" + "，".join(names)
    )
    await find_operator.finish(result_text.strip())


@random_operator.handle()
async def handle_random_operator(event: Event, args: Message[Any] = CommandArg()):
    user_id = event.get_user_id()
    current_data = find_operator_sessions.get(user_id, None)

    if current_data is None:
        await random_operator.finish(
            "【随机选择干员命令说明】\n"
            "使用方法：\n"
            "/随机选择 <数量>\n"
            "功能说明：\n"
            "1. 在筛选结果中随机选择指定数量的干员。\n"
            "2. 如果未指定数量，默认选择 1 个干员。\n"
            "注意：请先使用 /筛选 命令进行筛选后再使用此命令。"
        )

    reset_session_timeout(user_id)

    num_to_select = 1
    if args.extract_plain_text().strip():
        try:
            num_to_select = int(args.extract_plain_text().strip())
        except ValueError:
            await random_operator.finish("请输入一个有效的数字。")

    if num_to_select < 1:
        await random_operator.finish("请至少选择一个干员。")
    if num_to_select > len(current_data):
        await random_operator.finish(
            f"筛选结果中只有 {len(current_data)} 个干员，无法选择 {num_to_select} 个。"
        )

    import random

    selected_operators = random.sample(list(current_data.values()), num_to_select)
    selected_names: list[str] = [operator.get("name", "N/A") for operator in selected_operators]
    await random_operator.finish(f"随机选择的干员：{', '.join(selected_names)}")
