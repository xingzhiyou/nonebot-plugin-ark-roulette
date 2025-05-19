"""
资源文件 JSON 数据简易参考模型，不保证键值完整，静态检查器哈气时请自行确认并添加缺少的字段。
"""

from typing import NotRequired, TypedDict


class SubProfession(TypedDict):
    subProfessionId: str
    subProfessionName: str
    subProfessionCatagory: int


class UniEquipTable(TypedDict):
    subProfDict: dict[str, SubProfession]


class HandbookTeam(TypedDict):
    powerId: str
    orderNum: int
    powerLevel: int
    powerName: str
    powerCode: str
    color: str
    isLimited: bool
    isRaw: bool


class DisplaySkinInfo(TypedDict):
    modelName: str
    skinGroupName: str
    content: str
    drawerList: list[str] | None
    designerList: list[str] | None


class CharSkinInfo(TypedDict):
    skinId: str
    charId: str
    displaySkin: DisplaySkinInfo


class SkinTable(TypedDict):
    charSkins: dict[str, CharSkinInfo]


class BareFormattedSkinData(TypedDict):
    skinId: str
    modelName: str
    skinGroupName: str
    content: str
    drawerList: list[str] | None
    designerList: list[str] | None


class FormattedSkinData(BareFormattedSkinData, TypedDict):
    charId: str


class HandbookStoryStory(TypedDict):
    storyText: str


class HandbookStoryTextAudio(TypedDict):
    storyTitle: str
    stories: NotRequired[list[HandbookStoryStory]]


class HandbookData(TypedDict):
    storyTextAudio: list[HandbookStoryTextAudio]


class HandbookInfoTable(TypedDict):
    handbookDict: dict[str, HandbookData]


class CharacterInfo(TypedDict):
    name: str
    nationId: str | None
    groupId: str | None
    teamId: str | None
    displayNumber: str | None
    appellation: str
    profession: str
    tagList: list[str] | None
    itemObtainApproach: str | None
    rarity: str
    subProfessionId: str
    position: str


class MergedMapping(CharacterInfo):
    skins: list[BareFormattedSkinData]
    stories: dict[str, str]
