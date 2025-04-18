import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")
skin_table_path = os.path.join(DATA_DIR, "skin_table.json")

def load_skin_data(data_path):
    """
    从 skin_table.json 文件中提取 charSkins 表下的 charSkins 数据。
    """
    with open(data_path, "r", encoding="utf-8") as f:
        skin_data = json.load(f)
    
    # 提取 charSkins 数据
    char_skins = skin_data.get("charSkins", {})
    formatted_data = {}

    for skin_id, skin_info in char_skins.items():
        display_skin = skin_info.get("displaySkin", {})
        formatted_data[skin_id] = {
            "skinId": skin_info.get("skinId"),
            "charId": skin_info.get("charId"),
            "modelName": display_skin.get("modelName"),
            "skinGroupName": display_skin.get("skinGroupName"),
            "content": display_skin.get("content"),
            "drawerList": display_skin.get("drawerList"),
            "designerList": display_skin.get("designerList"),
        }
    
    return formatted_data
    


if __name__ == "__main__":
    skin_data = load_skin_data(skin_table_path)
    char_id = "char_002_amiya"
    matching_skins = {skin_id: data for skin_id, data in skin_data.items() if data["charId"] == char_id}
    x = []
    if matching_skins:
        print(f"皮肤数据 for {char_id}:")
        for skin_id, data in matching_skins.items():
            x.append(data["skinGroupName"])
    else:
        print(f"{char_id} not found in skin data.")

    print(x)
    print(len(x))