from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

CONFIG_PATH = Path("./config.yml")


class Config(BaseModel):
    db_url: str = "mysql+aiomysql://user:pwd@localhost/college"
    """mysql 地址"""
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"
    """日志等级"""

    secret_key: str = "82ec285b5f0670c852c2e16d9776c5d17bd89a5f1dc09cdab5374a8a9ec7aa11"
    """32 位 hex 密钥，可以通过类似于 openssl rand -hex 32 的命令获得"""
    algorithm: str = "HS256"
    """jwt 签名算法"""
    expire_minutes: int = 60
    """密钥过期时间"""


def load_config() -> Config:
    """
    加载配置文件
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("config.yml 不存在！请先创建")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader) or {}

    return Config(**config)


config = load_config()
