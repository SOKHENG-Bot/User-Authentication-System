from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.configuration.database import Base, engine
from app.controllers.user_controller import auth_router

from app.models.user_model import (
    User, PasswordResetToken, UserSession
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(lifespan=lifespan)


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])