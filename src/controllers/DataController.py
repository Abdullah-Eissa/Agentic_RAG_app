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
    
    
    async def calculate_uploadfile_hash(self, file: UploadFile, app_settings=None):
        
        sha256_hash = hashlib.sha256()
        
        await file.seek(0)
        
        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            sha256_hash.update(chunk)
            
        await file.seek(0)
        return sha256_hash.hexdigest()
    
    
    def calculate_local_file_hash(self, file_path: Path, app_settings=None) -> str:
        """Computes SHA-256 hash for a standard local file on disk."""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            while chunk := f.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                sha256_hash.update(chunk)
                
        return sha256_hash.hexdigest()
    
    # async def calculate_local_file_hash(self, file_path: Path, app_settings=None) -> str:
    #     """Computes SHA-256 hash for a standard local file on disk."""
    #     sha256_hash = hashlib.sha256()
        
    #     async with aiofiles.open(file_path, "rb") as f:
    #         while chunk := f.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
    #             sha256_hash.update(chunk)
                
    #     return sha256_hash.hexdigest()
    
    async def check_hashes(self, project_id, file: UploadFile, app_settings=None):
        
        upload_file_hash = await self.calculate_uploadfile_hash(file=file, app_settings=app_settings)
        
        project_controller = ProjectController()
    
        project_path = project_controller.get_project_path(project_id=project_id)
        
        # check hashes of all files in the project dir
        for file_path in Path(project_path).iterdir():
            
            if file_path.is_file():
                existing_file_hash = self.calculate_local_file_hash(file_path=file_path, app_settings=app_settings)
                
                if upload_file_hash == existing_file_hash:
                    return file_path
            
        return None