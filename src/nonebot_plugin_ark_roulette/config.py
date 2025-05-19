from pydantic import BaseModel


class Config(BaseModel, extra="ignore"):
    proxy: str | None = None
    """HTTPX proxy（代理）参数"""

    update_on_launch: bool = True
    """配置是否在启动时自动下载资源"""

# # 调用 rebuild() 确保类完全定义
# Config.model_rebuild()
