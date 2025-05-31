from src.stores.vectordb.providers import QdrantDBProvider
from src.stores.vectordb.VectorDBEnums import VectorDBEnums

class VectorDBProviderFactory:

    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            return QdrantDBProvider (
                db_path= self.config.VECTOR_DB_PATH,
                distance_method= None
            )
