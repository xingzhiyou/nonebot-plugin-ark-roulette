from pydantic import BaseModel

class Config(BaseModel):
    proxy: str = ""
    data_dir: str = "./data/arkrsc"