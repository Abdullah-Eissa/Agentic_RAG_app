from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os

class ProjectController(BaseController):
    
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        
        project_id = str(project_id)
        project_dir = os.path.join(
            self.files_dir,
            project_id
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir

    def get_file_path(self, project_id: str, file_id: str):
        project_dir = self.get_project_path(project_id=project_id)
        
        file_path = os.path.join(
            project_dir,
            file_id
        )
        
        if not os.path.exists(file_path):
            return None
        
        return file_path