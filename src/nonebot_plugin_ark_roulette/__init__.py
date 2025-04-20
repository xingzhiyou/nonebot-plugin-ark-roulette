import os
import json
import asyncio
from nonebot.plugin import PluginMetadata
from nonebot import on_command, logger
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg

from .ArkSrc import fetch_and_save_data_multithreaded
from .saveData import load_character_data, load_handbook_data, load_skin_data, merge_data, save_to_json
from .utils import map_tables, search_raw_data
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="明日方舟干员插件",
    description="提供明日方舟干员筛选与随机选择功能的插件。",
    usage="使用 /筛选 或 /随机选择 命令来获取干员信息。",
    type="application",
    homepage="https://github.com/xingzhiyou/nonebot-plugin-ark-roulette",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

confi = Config()
DATA_DIR = confi.data_dir
skin_table_path = os.path.join(DATA_DIR, "skin_table.json")
character_table_path = os.path.join(DATA_DIR, "character_table.json")
handbook_info_table_path = os.path.join(DATA_DIR, "handbook_info_table.json")
merged_character_data_path = os.path.join(DATA_DIR, "merged_character_data.json")

find_operator = on_command("筛选", aliases={"筛选干员"}, priority=5, block=True)
random_operator = on_command("随机选择", aliases={"随机干员", "roll"}, priority=5, block=True)
update_data = on_command("更新数据", aliases={"更新干员数据"}, priority=5, block=True, permission=SUPERUSER)

find_operator_sessions = {}
SESSION_TIMEOUT = 120
session_timeout_tasks = {}

def reset_session_timeout(user_id: str):
    if user_id in session_timeout_tasks:
        session_timeout_tasks[user_id].cancel()

    async def session_timeout():
        try:
            await asyncio.sleep(SESSION_TIMEOUT)
            logger.info(f"用户 {user_id} 的筛选会话超时，自动退出筛选模式。")
            find_operator_sessions.pop(f"find_operator_{user_id}", None)
            find_operator_sessions.pop(f"find_operator_history_{user_id}", None)
            session_timeout_tasks.pop(user_id, None)
            await find_operator.finish("由于长时间未操作，已自动退出筛选模式。")
        except FinishedException:
            pass

    session_timeout_tasks[user_id] = asyncio.create_task(session_timeout())

@update_data.handle()
async def handle_update_data():
    try:
        logger.info("开始更新干员数据...")
        await update_data.send("正在更新干员数据，请稍等...")
        fetch_and_save_data_multithreaded(DATA_DIR)
        merged_data = merge_data(
            load_character_data(character_table_path),
            load_handbook_data(handbook_info_table_path),
            load_skin_data(skin_table_path),
        )
        save_to_json(merged_data, merged_character_data_path)
        logger.info("干员数据更新完成！")
        await update_data.send("干员数据更新完成！")
    except Exception as e:
        logger.exception("更新数据时发生错误：")
        await update_data.send("更新数据失败，请检查日志。")

@find_operator.handle()
async def handle_find_operator(event: MessageEvent, args: Message = CommandArg()):
    user_id = event.get_user_id()
    session_key = f"find_operator_{user_id}"
    history_key = f"find_operator_history_{user_id}"

    if not os.path.exists(merged_character_data_path):
        await find_operator.finish("资源文件不存在，请使用 /更新数据 命令获取最新的干员数据后再尝试。")

    if session_key not in find_operator_sessions:
        with open(merged_character_data_path, "r", encoding="utf-8") as f:
            find_operator_sessions[session_key] = json.load(f)
        find_operator_sessions[history_key] = []

    current_data = find_operator_sessions[session_key]
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

    if keywords.lower() == 'q':
        find_operator_sessions.pop(session_key, None)
        find_operator_sessions.pop(history_key, None)
        session_timeout_tasks.pop(user_id, None).cancel()
        await find_operator.finish("已退出筛选模式。")
    elif keywords.lower() == 'r':
        with open(merged_character_data_path, "r", encoding="utf-8") as f:
            find_operator_sessions[session_key] = json.load(f)
        find_operator_sessions[history_key] = []
        await find_operator.finish("搜索结果已重置为完整数据集。")
    elif keywords.lower() == 'd':
        if find_operator_sessions[history_key]:
            find_operator_sessions[session_key] = find_operator_sessions[history_key].pop()
            await find_operator.finish("已撤销上一个关键词筛选。")
        else:
            await find_operator.finish("没有可以撤销的筛选操作。")

    keyword_list = keywords.split()
    find_operator_sessions[history_key].append(current_data.copy())

    for keyword in keyword_list:
        keyword = map_tables(keyword)
        results = search_raw_data(current_data, keyword)
        if results:
            current_data = {key: value for result in results for key, value in result.items()}
        else:
            await find_operator.finish(f"没有找到包含关键词 '{' '.join(keyword_list)}' 的条目。")

    find_operator_sessions[session_key] = current_data
    names = [value.get('name', 'N/A') for key, value in current_data.items()]
    result_text = f"找到 {len(current_data)} 个包含关键词 '{' '.join(keyword_list)}' 的条目：\n" + "，".join(names)
    await find_operator.finish(result_text.strip())

@random_operator.handle()
async def handle_random_operator(event: MessageEvent, args: Message = CommandArg()):
    user_id = event.get_user_id()
    session_key = f"find_operator_{user_id}"
    current_data = find_operator_sessions.get(session_key, None)

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
        await random_operator.finish(f"筛选结果中只有 {len(current_data)} 个干员，无法选择 {num_to_select} 个。")

    import random
    selected_operators = random.sample(list(current_data.values()), num_to_select)
    selected_names = [operator.get('name', 'N/A') for operator in selected_operators]
    await random_operator.finish(f"随机选择的干员：{', '.join(selected_names)}")
