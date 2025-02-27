import os
from typing import List, Dict
from database import Database

class FileManager:
    def __init__(self, database: Database):
        self.database = database
        self.project_directory = None
        self.result_directory = None
        
    def set_project_directory(self, directory: str):
        """设置工程目录"""
        self.project_directory = directory
    
    def set_result_directory(self, directory: str):
        """设置结果存储目录"""
        self.result_directory = directory
    
    def get_result_directory(self) -> str:
        """获取结果存储目录，如果未设置则使用工程目录"""
        return self.result_directory or self.project_directory
        
    def get_file_tree(self) -> Dict:
        """获取文件树结构"""
        if not self.project_directory:
            return {}
            
        tree = {}
        for root, dirs, files in os.walk(self.project_directory):
            # 跳过隐藏文件和目录和res目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'res']
            files = [f for f in files if not f.startswith('.') and f != 'res']
            
            relative_path = os.path.relpath(root, self.project_directory)
            current_level = tree
            
            if relative_path != '.':
                path_parts = relative_path.split(os.sep)
                for part in path_parts:
                    current_level = current_level.setdefault(part, {})
                    
            for file in files:
                current_level[file] = None
                
        return tree
        
    def get_changed_files(self) -> List[str]:
        """获取已更改的文件列表"""
        if not self.project_directory:
            return []
            
        changed_files = []
        for root, _, files in os.walk(self.project_directory):
            # 跳过res目录下的所有文件
            if 'res' in root.split(os.sep):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    current_content = f.read()
                    
                stored_content = self.database.get_latest_version(file_path)
                if stored_content is None or stored_content != current_content:
                    changed_files.append(file_path)
                    
        return changed_files
        
    def save_current_version(self, file_path: str):
        """保存文件当前版本"""
        if not os.path.exists(file_path):
            return
            
        with open(file_path, 'rb') as f:
            content = f.read()
            self.database.save_file_version(file_path, content)

    def get_all_files(self) -> List[str]:
        """获取所有文件列表"""
        if not self.project_directory:
            return []
        
        all_files = []
        for root, _, files in os.walk(self.project_directory):
            for file in files:
                if not file.startswith('.'):  # 跳过隐藏文件
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
        
        return all_files 