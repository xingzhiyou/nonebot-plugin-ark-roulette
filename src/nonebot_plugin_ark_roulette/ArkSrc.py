import asyncio
import json

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

    _ = (DATA_DIR / f"{name}.json").write_text(json.dumps(result), "utf-8")

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
