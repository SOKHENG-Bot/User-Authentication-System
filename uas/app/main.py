from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.configuration.database import Base, async_engine
from app.controllers.user_controller import admin_router, auth_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["User Management"])
app.include_router(admin_router, prefix="/sessions", tags=["Admin Management"])
