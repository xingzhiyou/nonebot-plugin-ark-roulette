import os
from nonebot import get_plugin_config
import httpx
import json
import asyncio
from .config import Config

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

DATA_DIR = conf.data_dir  # 从配置中获取数据目录

# 定义代理
PROXIES = conf.proxy  # 代理设置，格式为 {"http": "http://user:pass@proxy:port", "https": "https://user:pass@proxy:port"}


async def fetch_data(name, url, mirror_url, proxies, data_dir):
    """
    异步下载数据并保存到文件。
    """
    file_path = os.path.join(data_dir, f"{name}.json")
    async with httpx.AsyncClient(proxies=proxies) as client:
        try:
            # 从主站获取数据
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.RequestError:
            # 如果主站失败，尝试从镜像站获取
            if mirror_url:
                response = await client.get(mirror_url)
                response.raise_for_status()
                data = response.json()
            else:
                raise Exception(f"镜像站未定义 {name} 的 URL")

    # 将数据保存到文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return f"{name} 数据已成功保存到 {file_path}"

async def fetch_and_save_data_multithreaded(data_dir):
    """
    使用异步并发下载和保存数据。
    """
    # 确保 data 目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    tasks = [
        fetch_data(name, url, MIRROR_URLS.get(name), PROXIES, data_dir)
        for name, url in URLS.items()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results

# 示例用法
if __name__ == "__main__":
    # 使用 asyncio.run 运行异步主函数
    results = asyncio.run(fetch_and_save_data_multithreaded(DATA_DIR))
    for result in results:
        print(result)
    print("数据更新完成！")

