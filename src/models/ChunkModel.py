from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.model_dump())
        chunk.id = result.inserted_id

        return chunk

    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({
            "id" : ObjectId(chunk_id)
        })

        if result is None:
            return None

        return DataChunk(**result)

    async def insert_many_chunks(self, chunks: list, batch_size: int= 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i+batch_size]
            operations = [
                InsertOne(chunk.model_dump())
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: object):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count



