from nonebot import require

from .schemas import FormattedSkinData, SkinTable
from .utils import require_json

_ = require("nonebot_plugin_localstore")

from nonebot_plugin_localstore import get_plugin_data_dir

DATA_DIR = get_plugin_data_dir()


@require_json(DATA_DIR / "skin_table.json")
def load_skin_data(skin_data: SkinTable):
    """
    从 skin_table.json 文件中提取 charSkins 表下的 charSkins 数据。
    """

    # 提取 charSkins 数据
    char_skins = skin_data.get("charSkins", {})
    formatted_data: dict[str, FormattedSkinData] = {}

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
    skin_data = load_skin_data()
    char_id = "char_002_amiya"
    matching_skins = {skin_id: data for skin_id, data in skin_data.items() if data["charId"] == char_id}
    x: list[str] = []
    if matching_skins:
        print(f"皮肤数据 for {char_id}:")  # noqa: T201  # print in standalone mode
        for skin_id, data in matching_skins.items():
            x.append(data["skinGroupName"])
    else:
        print(f"{char_id} not found in skin data.")  # noqa: T201

    print(x)  # noqa: T201
    print(len(x))  # noqa: T201
