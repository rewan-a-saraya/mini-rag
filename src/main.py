from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings

@asynccontextmanager
async def lifespan(fastapi_app):
    settings = get_settings()
    fastapi_app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    fastapi_app.db_client = fastapi_app.mongo_conn[settings.MONGODB_DATABASE]

    print("MongoDB connected")
    yield
    fastapi_app.mongo_conn.close()
    print("MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)


# uvicorn src.main:app --reload
