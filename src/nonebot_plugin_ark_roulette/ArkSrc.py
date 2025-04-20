import os
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import Config

confi = Config()  # 实例化配置类

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

DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")

# 定义代理
PROXIES = confi.proxy  # 从配置中获取代理设置

def fetch_data(name, url, mirror_url, proxies, data_dir):
    """
    下载数据并保存到文件。
    """
    file_path = os.path.join(data_dir, f"{name}.json")
    try:
        # 从主站获取数据
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        # 如果主站失败，尝试从镜像站获取
        if mirror_url:
            response = requests.get(mirror_url, proxies=proxies)
            response.raise_for_status()
            data = response.json()
        else:
            raise Exception(f"镜像站未定义 {name} 的 URL")

    # 将数据保存到文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return f"{name} 数据已成功保存到 {file_path}"

def fetch_and_save_data_multithreaded(data_dir):
    """
    使用多线程下载和保存数据。
    """
    # 确保 data 目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    results = []  # 用于存储每个文件的处理结果
    with ThreadPoolExecutor() as executor:
        future_to_name = {
            executor.submit(fetch_data, name, url, MIRROR_URLS.get(name), PROXIES, data_dir): name
            for name, url in URLS.items()
        }

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(f"{name} 数据下载失败：{e}")

    return results

# 示例用法
if __name__ == "__main__":
    results = fetch_and_save_data_multithreaded(DATA_DIR)
    for result in results:
        print(result)
    print("数据更新完成！")

