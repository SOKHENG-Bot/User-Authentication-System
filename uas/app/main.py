from contextlib import asynccontextmanager

from app.configuration.database import Base, engine
from app.controllers.user_controller import auth_router, user_router
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/user", tags=["User Management"])
