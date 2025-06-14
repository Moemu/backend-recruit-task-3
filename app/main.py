from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, student, teacher
from app.api.admin import course, department, major, user
from app.core.config import config
from app.core.logger import logger
from app.core.sql import close_db, load_db

logger.info("初始化 Server...")


# 启动/关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_db()
    yield
    logger.info("正在退出...")
    await close_db()  # type:ignore
    logger.info("已安全退出")


app = FastAPI(title=config.title, version=config.version, lifespan=lifespan)


# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(student.router, prefix="/api/student", tags=["student"])
app.include_router(teacher.router, prefix="/api/course", tags=["course"])
app.include_router(user.router, prefix="/api/admin/user", tags=["admin", "user"])
app.include_router(
    department.router, prefix="/api/admin/department", tags=["admin", "department"]
)
app.include_router(major.router, prefix="/api/admin/major", tags=["admin", "major"])
app.include_router(course.router, prefix="/api/admin/course", tags=["admin", "course"])


if __name__ == "__main__":
    import uvicorn

    logger.info(f"服务器地址: http://{config.host}:{config.port}")
    logger.info(f"FastAPI 文档地址: http://{config.host}:{config.port}/docs")
    uvicorn.run(app, host=config.host, port=config.port)
