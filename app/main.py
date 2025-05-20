from api import auth
from fastapi import FastAPI

# from app.core.config import settings
# from app.utils.exceptions import register_exception_handlers  # 可选

app = FastAPI(title="Edu System", version="1.0.0")

# 注册异常处理器（可选）
# register_exception_handlers(app)

# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(student.router, prefix="/api/students", tags=["Students"])
# app.include_router(teacher.router, prefix="/api/teachers", tags=["Teachers"])
# app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# 启动/关闭事件（可选）
# @app.on_event("startup")
# async def startup_event():
#     print("🚀 教务系统启动")

# @app.on_event("shutdown")
# async def shutdown_event():
#     print("🛑 教务系统关闭")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
