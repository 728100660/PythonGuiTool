import os
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from database import Database

class FileManager:
    def __init__(self, database: Database):
        self.database = database
        self.project_directory = None
        self.result_directory = None
        self.save_queue = queue.Queue()
        self.save_thread = None
        self.is_saving = False
        
    def set_project_directory(self, directory: str):
        """设置工程目录"""
        self.project_directory = directory
    
    def set_result_directory(self, directory: str):
        """设置结果存储目录"""
        self.result_directory = directory
    
    def get_result_directory(self) -> str:
        """获取结果存储目录，如果未设置则使用默认目录"""
        if self.result_directory:
            return self.result_directory
        elif self.project_directory:
            # 默认在工程目录同级创建 test_results 目录
            default_dir = os.path.join(os.path.dirname(self.project_directory), 'test_results')
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
        return None
        
    def get_file_tree(self) -> Dict:
        """获取文件树结构"""
        if not self.project_directory:
            return {}
            
        tree = {}
        for root, dirs, files in os.walk(self.project_directory):
            # 跳过隐藏文件和目录和res目录
            dirs[:] = get_show_dirs(dirs)
            files = get_show_files(files)
            
            relative_path = os.path.relpath(root, self.project_directory)
            
            if not is_show_path(relative_path):
                continue
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
        all_file_paths = []
        for root, _, files in os.walk(self.project_directory):
            files = get_show_files(files)
            relative_path = os.path.relpath(root, self.project_directory)

            if not is_show_path(relative_path):
                continue

            all_file_paths.extend([os.path.join(root, file) for file in files])

        self.check_update_change_files(changed_files, all_file_paths)

        return changed_files

    def check_update_change_files(self, changed_files, file_paths):
        # 创建线程池，设置最大线程数为5
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有查询任务
            future_to_path = {executor.submit(self.database.get_latest_version, path): path for path in file_paths}

            # 按完成顺序处理结果
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                try:
                    stored_content = future.result()  # 获取查询结果

                    with open(file_path, 'rb') as f:
                        current_content = f.read()

                    stored_content = self.database.get_latest_version(file_path)
                    if stored_content is None or stored_content != current_content:
                        changed_files.append(file_path)
                except Exception as e:
                    print(f"Error processing {stored_content}: {e}")
        
    def start_save_thread(self):
        """启动保存线程"""
        if self.save_thread is None or not self.save_thread.is_alive():
            self.is_saving = True
            self.save_thread = threading.Thread(target=self._save_worker)
            self.save_thread.daemon = True
            self.save_thread.start()
    
    def _save_worker(self):
        """文件保存工作线程"""
        while self.is_saving:
            try:
                file_path = self.save_queue.get(timeout=1)  # 1秒超时
                if file_path == "STOP":
                    break
                    
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        self.database.save_file_version(file_path, content)
                
                self.save_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error saving file {file_path}: {e}")
    
    def stop_save_thread(self):
        """停止保存线程"""
        if self.save_thread and self.save_thread.is_alive():
            self.is_saving = False
            self.save_queue.put("STOP")
            self.save_thread.join()
    
    def save_current_version(self, file_path: str):
        """异步保存文件当前版本"""
        self.save_queue.put(file_path)
        self.start_save_thread()

    def get_all_files(self) -> List[str]:
        """获取所有文件列表"""
        if not self.project_directory:
            return []
        
        all_files = []
        for root, _, files in os.walk(self.project_directory):
            files = get_show_files(files)
            relative_path = os.path.relpath(root, self.project_directory)

            if not is_show_path(relative_path):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        
        return all_files


def get_show_dirs(dirs):
    return [d for d in dirs if not d.startswith('.')]


def is_show_path(path):
    return 'stage' in path


def get_show_files(files):
    return [f for f in files if not f.startswith('.') and f.endswith('.xlsx')]