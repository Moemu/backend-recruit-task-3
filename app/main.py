from contextlib import asynccontextmanager

from api import auth, student, teacher
from core.config import config
from core.sql import close_db, load_db
from fastapi import FastAPI


# 启动/关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_db()
    yield
    await close_db()


app = FastAPI(title=config.title, version=config.version, lifespan=lifespan)


# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(student.router, prefix="/api/student", tags=["student"])
app.include_router(teacher.router, prefix="/api/course", tags=["course"])
# app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.host, port=config.port)
