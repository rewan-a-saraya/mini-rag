from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from src.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from src.stores.llm.templates.template_parser import TemplateParser

@asynccontextmanager
async def lifespan(fastapi_app):
    settings = get_settings()
    fastapi_app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    fastapi_app.db_client = fastapi_app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    #generation client
    fastapi_app.generation_client = llm_provider_factory.create(provider = settings.GENERATION_BACKEND)
    fastapi_app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    #embedding client
    fastapi_app.embedding_client = llm_provider_factory.create(provider = settings.EMBEDDING_BACKEND)
    fastapi_app.embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID,
                                             embedding_size = settings.EMBEDDING_MODEL_SIZE)

    # vector db client
    fastapi_app.vectordb_client = vectordb_provider_factory.create(
        provider = settings.VECTOR_DB_BACKEND
    )
    fastapi_app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE,
    )

    print("MongoDB connected")
    yield
    fastapi_app.mongo_conn.close()
    print("MongoDB connection closed")


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)


# uvicorn src.main:app --reload