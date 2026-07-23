from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums import AssetTypeEnum
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_asset(self, asset: Asset):
        try:
            async with self.db_client() as session:
                async with session.begin():
                    session.add(asset)
                await session.commit()
                await session.refresh(asset)
            return asset
        
        except IntegrityError as e:
            return None

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str=AssetTypeEnum.FILE.value):

        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_type == asset_type
            )
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records

    async def get_asset_record(self, asset_project_id: str, asset_name: str):

        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_name == asset_name
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
        return record
    
    async def get_asset_by_hash(self, asset_project_id: int, file_hash: str):
        
        if asset_project_id is None or file_hash is None:
            return None

        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.file_hash == file_hash
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
        return record


    async def delete_asset_by_id(self, asset_id: int):
        async with self.db_client() as session:
            stmt = delete(Asset).where(Asset.asset_id == asset_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount


    async def delete_asset_by_hash(self, asset_project_id: int, file_hash: str):
        async with self.db_client() as session:
            stmt = delete(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.file_hash == file_hash
            )
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    
    async def delete_project_assets(self, asset_project_id: int):
        async with self.db_client() as session:
            stmt = delete(Asset).where(Asset.asset_project_id == asset_project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    
    async def update_asset_object(self, asset: Asset, new_asset_name: str, new_file_path: str):
        """Updates the asset_name and file_path of a given Asset instance and persists changes."""
        try:
            async with self.db_client() as session:
                # 1. Assign the new values to the object
                asset.asset_name = new_asset_name
                asset.file_path = new_file_path

                # 2. Merge the detached, modified object into the active session
                updated_asset = await session.merge(asset)

                # 3. Commit and refresh the merged instance
                await session.commit()
                await session.refresh(updated_asset)
                return updated_asset

        except IntegrityError:
            # Triggers if (asset_project_id, new_asset_name) violates the unique constraint
            return None