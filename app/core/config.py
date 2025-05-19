from pydantic import BaseModel
from pathlib import Path
from typing import Literal
import yaml

CONFIG_PATH = Path("./config.yaml")

class Config(BaseModel):
    db_url: str = "mysql://user:pwd@localhost/college"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"

def load_config() -> Config:
    """
    加载配置文件
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("config.yml 不存在！请先创建")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return Config(**config)

config = load_config()