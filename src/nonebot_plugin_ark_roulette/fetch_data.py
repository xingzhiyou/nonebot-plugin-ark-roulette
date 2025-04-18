import os
import requests
import json

# 定义目标 URL 和保存路径
URLS = {
    "character_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/character_table.json",
    "handbook_team_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/handbook_team_table.json",
    "uniequip_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/uniequip_table.json",
    "skin_table": "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/refs/heads/master/zh_CN/gamedata/excel/skin_table.json",
}
DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")

def fetch_and_save_data(DATA_DIR):
    # 确保 data 目录存在
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    for name, url in URLS.items():
        file_path = os.path.join(DATA_DIR, f"{name}.json")
        try:
            # 从 URL 获取数据
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()

            # 将数据保存到文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            return(f"{name} 数据已成功保存到 {file_path}")
        except requests.RequestException as e:
            return(f"请求 {name} 数据失败：{e}")
        except Exception as e:
            return(f"保存 {name} 数据时发生错误：{e}")

def get_drawer_list_from_skin_table(skin_table_path, drawer_list=None):
    """
    从 skin_table.json 文件中根据 drawerList 搜索对应的 charId 列表。
    """
    with open(skin_table_path, "r", encoding="utf-8") as f:
        skin_data = json.load(f)
    
    # 提取所有符合 drawerList 的 charId
    matching_char_ids = set()
    for skin_id, skin_info in skin_data.get("charSkins", {}).items():
        # 获取 displaySkin 中的 drawerList
        display_skin = skin_info.get("displaySkin", {})
        if not display_skin:  # 检查 displaySkin 是否为 None 或空
            continue
        
        skin_drawer_list = display_skin.get("drawerList", [])
        if not isinstance(skin_drawer_list, list):  # 确保 drawerList 是列表
            continue
        
        # 检查 drawerList 是否匹配
        if drawer_list and any(drawer in skin_drawer_list for drawer in drawer_list):
            char_id = skin_info.get("charId")
            matching_char_ids.add(char_id)
    
    return matching_char_ids

def find_matching_characters(character_table_path, search_criteria, drawer_list=None):
    """
    从 character_table.json 文件中寻找符合条件的角色。
    """
    with open(character_table_path, "r", encoding="utf-8") as f:
        character_data = json.load(f)
    
    matching_characters = []
    for char_id, char_info in character_data.items():
        # 如果提供了 drawer_list，则过滤角色 ID
        if drawer_list and char_id not in drawer_list:
            continue
        
        # 检查是否满足所有搜索条件
        match = True
        for field, value in search_criteria.items():
            if field in char_info:
                if char_info[field] != value:
                    match = False
                    break
            else:
                match = False
                break
        
        if match:
            # 保留完整的角色信息
            matching_characters.append(char_info)
    
    return matching_characters

# 示例用法
if __name__ == "__main__":
    
    search_criteria = {
        # "rarity": "TIER_4",
        # "profession": "Caster",
    }

    drawer_list = ["HUG"]

    skin_table_path = os.path.join(DATA_DIR, "skin_table.json")
    character_table_path = os.path.join(DATA_DIR, "character_table.json")

    # 获取符合 drawerList 的 charId 列表
    matching_drawer_list = get_drawer_list_from_skin_table(skin_table_path, drawer_list)
    matc = find_matching_characters(character_table_path, search_criteria, matching_drawer_list)
    print("符合条件的角色：")
    for character in matc:
        print(character)

    
