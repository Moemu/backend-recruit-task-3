from datetime import datetime

import sqlalchemy
from sqlalchemy import (
    BigInteger,
    DateTime,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    dept_no: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, comment="院系编号"
    )
    dept_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="院系名称"
    )
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        comment="创建时间",
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
        comment="更新时间",
    )
