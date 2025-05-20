from pydantic import BaseModel


class Token(BaseModel):
    """
    jwt 密钥实体
    """

    access_token: str
    token_type: str
