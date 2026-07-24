from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from sqlalchemy.future import select
from sqlalchemy import func, delete
from sqlalchemy.dialects.postgresql import insert

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_chunk(self, chunk: DataChunk):

        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk

    async def get_chunk(self, chunk_id: str):

        async with self.db_client() as session:
            result = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
            chunk = result.scalar_one_or_none()
        return chunk


    # async def insert_many_chunks(self, chunks: list, batch_size: int=100):

    #     async with self.db_client() as session:
    #         async with session.begin():
    #             for i in range(0, len(chunks), batch_size):
    #                 batch = chunks[i:i+batch_size]
    #                 session.add_all(batch)
    #         await session.commit()
    #     return len(chunks)
        
    
    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 100) -> int:
        if not chunks:
            return 0

        seen_project_hashes, seen_asset_hashes = set(), set()
        unique_chunks = []

        for chunk in chunks:
            project_key = (chunk.chunk_project_id, chunk.chunk_hash)
            asset_key = (chunk.chunk_asset_id, chunk.chunk_hash)

            if project_key not in seen_project_hashes and asset_key not in seen_asset_hashes:
                seen_project_hashes.add(project_key)
                seen_asset_hashes.add(asset_key)
                unique_chunks.append(chunk)

        if not unique_chunks:
            return 0

        inserted_count = 0

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(unique_chunks), batch_size):
                    batch = unique_chunks[i : i + batch_size]
                    
                    values = [
                        {
                            # "chunk_uuid": c.chunk_uuid,
                            "chunk_text": c.chunk_text,
                            "chunk_hash": c.chunk_hash,
                            "chunk_metadata": c.chunk_metadata,
                            "chunk_order": c.chunk_order,
                            "chunk_project_id": c.chunk_project_id,
                            "chunk_asset_id": c.chunk_asset_id,
                        }
                        for c in batch
                    ]

                    # Target ALL unique constraints on the table (project_id, asset_id, uuid)
                    stmt = (
                        insert(DataChunk)
                        .values(values)
                        .on_conflict_do_nothing(constraint="uq_chunk_project_id_chunk_hash")
                    )

                    result = await session.execute(stmt)
                    inserted_count += result.rowcount  # Tracks only newly inserted rows

        return inserted_count
        

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    
    # async def delete_chunks_by_asset_id(self, asset_id: ObjectId):
    #     async with self.db_client() as session:
    #         stmt = delete(DataChunk).where(DataChunk.chunk_asset_id == asset_id)
    #         result = await session.execute(stmt)
    #         await session.commit()
    #     return result.rowcount
    
    async def get_poject_chunks(self, project_id: ObjectId, page_no: int=1, page_size: int=50):
        async with self.db_client() as session:
            stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records
    
    
    async def get_project_chunks_total_count(self, chunk_project_id: int):
        async with self.db_client() as session:
            stmt = (
                select(func.count(DataChunk.chunk_id))
                .where(DataChunk.chunk_project_id == chunk_project_id)
            )
            total_count = await session.scalar(stmt)
            return total_count