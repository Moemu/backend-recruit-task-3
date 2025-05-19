import sqlalchemy
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Enum, Integer
from sqlalchemy.orm import relationship, DeclarativeBase as Base
import enum

META = sqlalchemy.MetaData()


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名"),
    password = Column(String(100), nullable=False, comment="密码"),
    role = Column(Enum(UserRole), nullable=False, comment="角色(ADMIN/TEACHER/STUDENT)"),
    status = Column(Boolean, nullable=False, default=0, comment="状态(0-正常,1-禁用)"),
    create_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), comment="创建时间"),
    update_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), comment="更新时间"),

class Student(User):
    __tablename__ = "Student"

    major_id = Column(BigInteger, nullable=False, comment="专业ID")
    grade = Column(Integer, nullable=False, comment="年级")


class Course(Base):
    __tablename__ = "course"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    course_no = Column(String(20), unique=True, nullable=False, comment="课程编号")
    course_name = Column(String(50), nullable=False, comment="课程名称")
    teacher_id = Column(BigInteger, nullable=False, comment="教师ID")
    major_id = Column(BigInteger, nullable=False, comment="专业ID")
    grade = Column(Integer, nullable=False, comment="年级")
    course_type = Column(Integer, nullable=False, comment="课程类型(0-必修, 1-选修)")
    credit = Column(String(10), nullable=False, comment="学分")
    is_public = Column(Boolean, nullable=False, default=0, comment="是否公开(0-否,1-是)")
    status = Column(Boolean, nullable=False, default=0, comment="状态(0-正常,1-禁用)")
    create_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), comment="更新时间")

class Department(Base):
    __tablename__ = "department"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    dept_no = Column(String(10), unique=True, nullable=False, comment="院系编号")
    dept_name = Column(String(50), nullable=False, comment="院系名称")
    create_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), comment="更新时间")

class Major(Base):
    __tablename__ = "major"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    major_no = Column(String(10), unique=True, nullable=False, comment="专业编号")
    major_name = Column(String(50), nullable=False, comment="专业名称")
    dept_id = Column(BigInteger, nullable=False, comment="院系ID")
    create_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), comment="更新时间")