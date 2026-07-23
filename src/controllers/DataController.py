from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
import aiofiles
import hashlib
import os
from pathlib import Path
from models import ResponseSignal
import re
import os

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 # convert MB to bytes

    def validate_uploaded_file(self, file: UploadFile):

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale: # convert from MB to Byte
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filepath(self, orig_file_name: str, project_id: str):

        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id) # get project path by the id like 1, 2, 3 and so on.

        cleaned_file_name = self.get_clean_file_name(
            orig_file_name=orig_file_name
        )

        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name

    
    async def calculate_uploadfile_hash(self, file: UploadFile):
        
        sha256_hash = hashlib.sha256()
        await file.seek(0)
        
        while chunk := await file.read(self.app_settings.FILE_DEFAULT_CHUNK_SIZE):
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            sha256_hash.update(chunk)
            
        await file.seek(0)
        return sha256_hash.hexdigest()
    
    
    async def calculate_local_file_hash(self, file_path: Path):
        """Computes SHA-256 hash for a standard local file on disk."""
        
        if file_path is None:
            return None
        
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(Path(file_path), "rb") as f:
            while chunk := await f.read(self.app_settings.FILE_DEFAULT_CHUNK_SIZE):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    async def check_duplicate_files(self, project_id, asset_model, uploadfile: UploadFile): # take all project assets
        
        upload_file_hash = await self.calculate_uploadfile_hash(file=uploadfile)
        
        # compare the uploaded file hash with all hashes in assets database
        result = await asset_model.get_asset_by_hash(asset_project_id=project_id, file_hash=upload_file_hash)
            
        return result
    
    async def sync_assets(self, project_id: int, project_dir: str, asset_model):
        """ 
        sync assets table with files folder as the following:
        1. if file hash not existed in assets table, then delete this file
        2. if the file hash existed in assets table, but repeated in the folder, then leave only the newest one
        3. if an asset hash not existed in files folder, then remove this asset
        """
        
        project_dir = Path(project_dir)
        
        if not project_dir.exists() or not project_dir.is_dir():
            return []
        
        if next(project_dir.iterdir(), None) is None:
            await asset_model.delete_project_assets(asset_project_id=project_id)
            return []
            
        
        # get all file paths and sort them by date from oldest to newest
        files_paths = [file_path for file_path in project_dir.iterdir() if file_path.is_file()]
        files_paths.sort(key=lambda f: f.stat().st_mtime)
        
        seen_hashes = {} # hash: file_path
        deleted_files = []
        for file_path in files_paths:
            
            file_hash = await self.calculate_local_file_hash(file_path=file_path)
            
            asset = await asset_model.get_asset_by_hash(asset_project_id=project_id, file_hash=file_hash)
            
            if asset is None: # if file hash not existed in assets table, delete it from files folder
                file_path.unlink(missing_ok=True)
                deleted_files.append(file_path.name)
                continue
            
            # if file existed in asset table
            if file_hash in seen_hashes: # oldest file seen before
                seen_hashes[file_hash].unlink(missing_ok=True)
                deleted_files.append(seen_hashes[file_hash].name)
                
            seen_hashes[file_hash] = file_path # put the newer one
            
            # Update asset asset_name and file_path
            asset = await asset_model.update_asset_object(
                    asset=asset,
                    new_asset_name=file_path.name,
                    new_file_path=str(file_path)
                )
        
        all_project_assets = await asset_model.get_all_project_assets(asset_project_id=project_id)
        
        if all_project_assets is not None: # if there is a hash in asset table not in the folder, then remove it
            asset_hashes = [asset.file_hash for asset in all_project_assets]
            
            for asset_file_hash in asset_hashes:
                
                if asset_file_hash not in seen_hashes:
                    await asset_model.delete_asset_by_hash(asset_project_id=project_id, file_hash=asset_file_hash)
            
        return deleted_files