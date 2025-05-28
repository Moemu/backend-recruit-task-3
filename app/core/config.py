import logging
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

CONFIG_PATH = Path("./config.yml")


class Config(BaseModel):
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"
    """日志等级"""

    # FastAPI 配置
    title: str = "ManagementSystem"
    """API 服务标题"""
    version: str = "0.1.0"
    """API 服务版本"""
    host: str = "127.0.0.1"
    """API 本地回环地址(IP地址)"""
    port: int = 8080
    """API 服务端口"""

    # jwt 配置
    secret_key: str = "82ec285b5f0670c852c2e16d9776c5d17bd89a5f1dc09cdab5374a8a9ec7aa11"
    """32 位 hex 密钥，可以通过类似于 openssl rand -hex 32 的命令获得"""
    algorithm: str = "HS256"
    """jwt 签名算法"""
    expire_minutes: int = 60
    """密钥过期时间"""

    # mysql 配置
    db_url: str = "mysql+aiomysql://user:pwd@localhost/college"
    """mysql 地址"""

    # redis 配置
    redis_host: str = "127.0.0.1"
    """redis 本地回环地址(IP地址)"""
    redis_port: int = 6379
    """redis 服务端口"""


def load_config() -> Config:
    """
    加载配置文件
    """
    config: dict = dict()

    if not CONFIG_PATH.exists():
        logging.warning("未找到 config.yml, 将使用默认配置，可能导致意外的后果!")
    else:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.load(f, Loader=yaml.FullLoader) or {}

    return Config(**config)


config = load_config()
