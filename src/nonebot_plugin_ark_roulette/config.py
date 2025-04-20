from pydantic import BaseModel
from typing import Set

class Config(BaseModel):
    proxy: str = ""
    data_dir: str = "data/arkrsc"