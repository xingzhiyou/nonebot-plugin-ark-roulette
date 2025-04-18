import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data/arkrsc")
handbook_info_table_path = os.path.join(DATA_DIR, "handbook_info_table.json")

def load_handbook(data_path):
    """
    从 handbook_info_table.json 文件中提取 handbookDict 表下的 storyTitle 和 storyText 数据。
    """
    with open(data_path, "r", encoding="utf-8") as f:
        handbook_data = json.load(f)
    
    # 提取 handbookDict 数据
    handbook_dict = handbook_data.get("handbookDict", {})
    formatted_data = {}

    for char_id, char_data in handbook_dict.items():
        if "storyTextAudio" in char_data:
            formatted_data[char_id] = {
                story["storyTitle"]: story["stories"][0]["storyText"]
                for story in char_data["storyTextAudio"]
                if "stories" in story and story["stories"]
            }
    
    return formatted_data


def retrieve_info(handbook_data, char_id, title, info_keyword):
    """
    根据角色 ID 和标题提取信息。
    """
    if char_id in handbook_data and title in handbook_data[char_id]:
        gender_info = handbook_data[char_id][title].split("\n")
        for info in gender_info:
            if info_keyword in info:
                return info.split("】")[-1].strip()
    return None

# 示例调用
if __name__ == "__main__":
    handbook_stories = load_handbook(handbook_info_table_path)
    for char_id, stories in handbook_stories.items():
        gender = retrieve_info(handbook_stories, char_id, "综合体检测试", "物理强度")
        print(f"角色 ID: {char_id}, 值: {gender}")
