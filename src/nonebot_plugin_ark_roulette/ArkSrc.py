import asyncio
import json
import os

import httpx
from nonebot import get_plugin_config, require

from .config import Config

_ = require("nonebot_plugin_localstore")

from nonebot_plugin_localstore import get_plugin_data_dir

DATA_DIR = get_plugin_data_dir()

conf = get_plugin_config(Config)


# 定义目标 URL 和保存路径
URLS = {
    "character_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/character_table.json",
    "handbook_team_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/handbook_team_table.json",
    "uniequip_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/uniequip_table.json",
    "skin_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/skin_table.json",
    "handbook_info_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/handbook_info_table.json",
}

# 定义备用镜像站 URL
MIRROR_URLS = {
    "character_table": "https://ghfast.top/https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/character_table.json",
    "handbook_team_table": "https://ghfast.top/https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/handbook_team_table.json",
    "uniequip_table": "https://ghfast.top/https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/uniequip_table.json",
    "skin_table": "https://ghfast.top/https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/skin_table.json",
    "handbook_info_table": "https://ghfast.top/https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/handbook_info_table.json",
}

# 定义代理
PROXIES = (
    conf.proxy
)  # 代理设置，格式为 {"http": "http://user:pass@proxy:port", "https": "https://user:pass@proxy:port"}


async def fetch_data(
    name: str, url: str, mirror_url: str | None, proxy: httpx.URL | str | httpx.Proxy | None
):
    """
    异步下载数据。
    """
    # 验证名称参数，防止目录遍历攻击
    if not name or any(char in name for char in '\\/:*?"<>|'):
        raise ValueError("Invalid file name")
    
    # 确保文件名安全，仅使用基本字符
    safe_name = ''.join(c for c in name if c.isalnum() or c in '_-')
    if not safe_name:
        raise ValueError("Invalid file name")
    
    async with httpx.AsyncClient(proxy=proxy) as client:
        try:
            # 从主站获取数据
            response = (await client.get(url)).raise_for_status()
            result = response.json()
        except httpx.RequestError:
            # 如果主站失败，尝试从镜像站获取
            if mirror_url:
                response = (await client.get(mirror_url)).raise_for_status()
                result = response.json()
            else:
                raise Exception(f"镜像站未定义 {name} 的 URL")

    # 安全构建文件路径，确保在DATA_DIR目录内
    file_path = DATA_DIR / f"{safe_name}.json"
    # 验证路径是否在DATA_DIR内，防止目录遍历
    if not str(file_path).startswith(str(DATA_DIR)):
        raise ValueError("Invalid file path")
    
    _ = file_path.write_text(json.dumps(result), "utf-8")

    return result


async def fetch_data_by_name(name: str, proxy: httpx.URL | str | httpx.Proxy | None):
    return await fetch_data(name, URLS[name], MIRROR_URLS.get(name), proxy)


async def fetch_and_save_data_async():
    """
    使用异步并发下载数据。
    """

    tasks = [fetch_data_by_name(name, PROXIES) for name in URLS]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    return results


def check_resource_exists():
    return all((DATA_DIR / f"{name}.json").is_file() for name in URLS)


# 示例用法
if __name__ == "__main__":
    # 使用 asyncio.run 运行异步主函数
    results = asyncio.run(fetch_and_save_data_async())

    for result in results:
        print(result)  # noqa: T201  # print in standalone mode

    print("数据更新完成！")  # noqa: T201
