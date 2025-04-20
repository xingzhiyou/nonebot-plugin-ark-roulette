import json
import os
import asyncio
from nonebot.plugin import PluginMetadata
from nonebot import on_command, logger, get_driver
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg

from .ArkSrc import fetch_and_save_data
from .mapping import FIELD_MAPPING, load_mappings
from .saveData import load_character_data, load_handbook_data, load_skin_data, merge_data, save_to_json
from .utils import map_tables, search_raw_data
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="明日方舟干员插件",
    description="提供明日方舟干员筛选与随机选择功能的插件。",
    usage="使用 /筛选 或 /随机选择 命令来获取干员信息。",
    type="application",
    homepage="https://github.com/xingzhiyou/nonebot-plugin-ark-roulette",
    config=Config,  # 插件配置类
    supported_adapters={"~onebot.v11"},  # 支持的适配器
)

confi = Config()  # 实例化配置类

# 定义数据目录和文件路径
DATA_DIR = confi.data_dir  # 从配置中获取数据目录
skin_table_path = os.path.join(DATA_DIR, "skin_table.json")
character_table_path = os.path.join(DATA_DIR, "character_table.json")
uniequip_table_path = os.path.join(DATA_DIR, "uniequip_table.json")
handbook_team_table_path = os.path.join(DATA_DIR, "handbook_team_table.json")
nation_table_path = os.path.join(DATA_DIR, "nation_table.json")
handbook_info_table_path = os.path.join(DATA_DIR, "handbook_info_table.json")
merged_character_data_path = os.path.join(DATA_DIR, "merged_character_data.json")

# 加载映射表和数据文件
mappings = load_mappings(uniequip_table_path, handbook_team_table_path)

find_operator = on_command("筛选", aliases={"筛选干员"}, priority=5, block=True)
random_operator = on_command("随机选择", aliases={"随机干员", "roll"}, priority=5, block=True)
update_data = on_command("更新数据", aliases={"更新干员数据"}, priority=5, block=True, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)

# 添加全局变量用于存储会话数据
find_operator_sessions = {}

# 定义超时时间（秒）
SESSION_TIMEOUT = 120

# 添加一个全局字典用于存储用户的超时任务
session_timeout_tasks = {}



# 定义一个函数来启动或重置超时任务
def reset_session_timeout(user_id: str):
    """
    重置用户的超时任务。
    """
    # 如果用户已有超时任务，取消旧任务
    if user_id in session_timeout_tasks:
        session_timeout_tasks[user_id].cancel()
    # 定义超时任务
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
    # 启动新的超时任务
    session_timeout_tasks[user_id] = asyncio.create_task(session_timeout())

@update_data.handle()
async def handle_update_data(bot: Bot, event: MessageEvent):
    """
    处理更新数据命令，异步执行资源更新。
    """
    try:
        logger.info("开始更新干员数据...")
        await update_data.send("正在更新干员数据，请稍等...")

        # 异步执行资源更新
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, update_resources)

        logger.info("干员数据更新完成！")
        await update_data.send("干员数据更新完成！")
    except FinishedException:
        logger.warning("更新数据命令被中断。")
        pass
    except Exception as e:
        logger.exception("更新数据时发生错误：")
        await update_data.send("更新数据失败，请检查日志。")


def update_resources():
    """
    同步执行资源更新的逻辑。
    """
    try:
        # 下载并保存数据
        logger.info("正在下载并保存干员数据...")
        fetch_and_save_data(DATA_DIR)

        # 加载数据文件
        logger.info("正在加载干员数据文件...")
        character_data = load_character_data(character_table_path)
        handbook_data = load_handbook_data(handbook_info_table_path)
        skin_data = load_skin_data(skin_table_path)

        # 合并数据
        logger.info("正在合并干员数据...")
        merged_data = merge_data(character_data, handbook_data, skin_data)

        # 保存合并后的数据
        logger.info("正在保存合并后的干员数据...")
        save_to_json(merged_data, os.path.join(DATA_DIR, "merged_character_data.json"))
    except Exception as e:
        logger.exception("更新资源时发生错误：")
        raise e


@find_operator.handle()
async def handle_find_operator(event: MessageEvent, args: Message = CommandArg()):
    """
    处理筛选干员命令，支持多次筛选、重置、删除上一个关键词，并支持一次输入多个关键词。
    """
    user_id = event.get_user_id()
    session_key = f"find_operator_{user_id}"
    history_key = f"find_operator_history_{user_id}"

    logger.info(f"用户 {user_id} 开始筛选操作，输入参数: {args.extract_plain_text().strip()}")

    # 检查资源文件是否存在
    if not os.path.exists(merged_character_data_path):
        logger.warning(f"资源文件 {merged_character_data_path} 不存在，提醒用户更新数据。")
        await find_operator.finish(
            "资源文件不存在，请使用 /更新数据 命令获取最新的干员数据后再尝试。"
        )

    # 初始化或获取用户的当前数据和历史记录
    if session_key not in find_operator_sessions:
        logger.info(f"用户 {user_id} 的会话数据不存在，初始化数据。")
        with open(merged_character_data_path, "r", encoding="utf-8") as f:
            find_operator_sessions[session_key] = json.load(f)
        find_operator_sessions[history_key] = []  # 初始化历史记录

    current_data = find_operator_sessions[session_key]
    keywords = args.extract_plain_text().strip()

    if not keywords:
        logger.warning(f"用户 {user_id} 未输入关键词，发送说明书。")
        usage_message = (
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
        await find_operator.finish(usage_message)

    # 在每个用户交互的逻辑分支中调用 reset_session_timeout
    if keywords.lower() == 'q':
        reset_session_timeout(user_id)  # 重置计时器
        logger.info(f"用户 {user_id} 退出筛选模式。")
        find_operator_sessions.pop(session_key, None)
        find_operator_sessions.pop(history_key, None)
        session_timeout_tasks.pop(user_id, None).cancel()  # 取消超时任务
        await find_operator.finish("已退出筛选模式。")
    elif keywords.lower() == 'r':
        reset_session_timeout(user_id)  # 重置计时器
        logger.info(f"用户 {user_id} 重置筛选结果。")
        with open(merged_character_data_path, "r", encoding="utf-8") as f:
            find_operator_sessions[session_key] = json.load(f)
        find_operator_sessions[history_key] = []  # 重置历史记录
        await find_operator.finish("搜索结果已重置为完整数据集。")
    elif keywords.lower() == 'd':
        reset_session_timeout(user_id)  # 重置计时器
        if find_operator_sessions[history_key]:
            logger.info(f"用户 {user_id} 撤销上一个关键词筛选。")
            # 回退到上一个状态
            find_operator_sessions[session_key] = find_operator_sessions[history_key].pop()
            await find_operator.finish("已撤销上一个关键词筛选。")
        else:
            logger.warning(f"用户 {user_id} 尝试撤销筛选，但没有历史记录。")
            await find_operator.finish("没有可以撤销的筛选操作。")

    # 在关键词处理逻辑中也调用 reset_session_timeout
    keyword_list = keywords.split()
    reset_session_timeout(user_id)  # 重置计时器
    logger.info(f"用户 {user_id} 输入的关键词列表: {keyword_list}")
    find_operator_sessions[history_key].append(current_data.copy())  # 保存当前数据到历史记录

    # 重新启动计时器
    reset_session_timeout(user_id)

    for keyword in keyword_list:
        # 使用映射表转换关键词
        logger.info(f"用户 {user_id} 正在处理关键词: {keyword}")
        keyword = map_tables(keyword)
        results = search_raw_data(current_data, keyword)
        if results:
            logger.info(f"用户 {user_id} 的关键词 '{keyword}' 找到 {len(results)} 个结果。")
            # 更新当前数据为本次搜索结果
            current_data = {key: value for result in results for key, value in result.items()}
        else:
            logger.warning(f"用户 {user_id} 的关键词 '{keyword}' 未找到结果。")
            # 如果没有找到结果，显示所有输入的关键词
            await find_operator.finish(f"没有找到包含关键词 '{' '.join(keyword_list)}' 的条目。")

    # 更新会话数据
    find_operator_sessions[session_key] = current_data
    # 提取所有结果的名称
    names = [value.get('name', 'N/A') for key, value in current_data.items()]
    result_text = f"找到 {len(current_data)} 个包含关键词 '{' '.join(keyword_list)}' 的条目：\n" + "，".join(names)
    logger.info(f"用户 {user_id} 的筛选结果: {result_text.strip()}")
    await find_operator.finish(result_text.strip())


@ random_operator.handle()
async def handle_random_operator(event: MessageEvent, args: Message = CommandArg()):
    """
    处理随机选择干员命令。
    """
    user_id = event.get_user_id()
    # 输出筛选后的表
    session_key = f"find_operator_{user_id}"
    history_key = f"find_operator_history_{user_id}"
    current_data = find_operator_sessions.get(session_key, None)

    if current_data is None:
        logger.warning(f"用户 {user_id} 尝试随机选择，但没有筛选结果。")
        usage_message = (
            "【随机选择干员命令说明】\n"
            "使用方法：\n"
            "/随机选择 <数量>\n"
            "功能说明：\n"
            "1. 在筛选结果中随机选择指定数量的干员。\n"
            "2. 如果未指定数量，默认选择 1 个干员。\n"
            "注意：请先使用 /筛选 命令进行筛选后再使用此命令。"
        )
        await random_operator.finish(usage_message)
        # 重置超时任务
        reset_session_timeout(user_id)


    # 随机选择指定数量的干员，默认一个
    import random
    user_id = event.get_user_id()
    reset_session_timeout(user_id)  # 重置计时器

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
    
    selected_operators = random.sample(list(current_data.values()), num_to_select)
    selected_names = [operator.get('name', 'N/A') for operator in selected_operators]
    await random_operator.finish(f"随机选择的干员：{', '.join(selected_names)}")