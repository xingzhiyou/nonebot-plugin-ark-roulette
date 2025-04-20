import os
import requests
import json
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

def fetch_and_save_data(DATA_DIR):
    # 确保 data 目录存在
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    results = []  # 用于存储每个文件的处理结果
    for name, url in URLS.items():
        file_path = os.path.join(DATA_DIR, f"{name}.json")
        try:
            # 从主站获取数据
            response = requests.get(url, proxies=PROXIES)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
        except requests.RequestException as e:
            # 如果主站失败，尝试从镜像站获取
            try:
                mirror_url = MIRROR_URLS.get(name)
                if mirror_url:
                    response = requests.get(mirror_url, proxies=PROXIES)
                    response.raise_for_status()
                    data = response.json()
                    results.append(f"从镜像站成功获取 {name} 数据")
                else:
                    raise Exception(f"镜像站未定义 {name} 的 URL")
            except Exception as mirror_e:
                results.append(f"请求 {name} 数据失败（主站和镜像站均失败）：{e}, {mirror_e}")
                continue

        try:
            # 将数据保存到文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            results.append(f"{name} 数据已成功保存到 {file_path}")
        except Exception as e:
            results.append(f"保存 {name} 数据时发生错误：{e}")
    
    return results  # 返回所有结果


# 示例用法
if __name__ == "__main__":
    results = fetch_and_save_data(DATA_DIR)
    for result in results:
        print(result)
    print("数据更新完成！")

