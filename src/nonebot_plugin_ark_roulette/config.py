from pydantic import BaseModel

class Config(BaseModel):
    proxy: str = ""
    data_dir: str = "./data/arkrsc"

# 调用 rebuild() 确保类完全定义
Config.model_rebuild()