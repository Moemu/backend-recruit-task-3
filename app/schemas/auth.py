from dataclasses import asdict, dataclass, field
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel


class Token(BaseModel):
    """
    jwt 密钥实体
    """

    access_token: str
    token_type: str


@dataclass
class Payload:
    """
    jwt Payload
    """

    sub: str
    """用户名"""
    exp: Optional[int] = None
    """过期时间"""
    jti: str = field(default_factory=lambda: uuid4().hex)
    """JWT ID"""

    def to_json(self):
        return asdict(self)
