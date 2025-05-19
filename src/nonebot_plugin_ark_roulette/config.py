from pydantic import BaseModel


class Config(BaseModel, extra="ignore"):
    proxy: str | None = None

    update_on_launch: bool = True

# # 调用 rebuild() 确保类完全定义
# Config.model_rebuild()
