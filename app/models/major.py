from datetime import datetime

import sqlalchemy
from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base


class Major(Base):
    __tablename__ = "major"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    major_no: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, comment="专业编号"
    )
    major_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="专业名称"
    )
    dept_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="院系ID")
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
