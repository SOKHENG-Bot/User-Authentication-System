from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Annotated
from fastapi import Depends

from app.configuration.settings import settings


engine = create_async_engine(
    settings.SQLITE_DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


db_session = Annotated[AsyncSessionLocal, Depends(get_db)]
