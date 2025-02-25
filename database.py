import sqlite3
import os
import hashlib
from datetime import datetime

class Database:
    def __init__(self):
        """初始化数据库连接"""
        self.db_path = "config_manager.db"
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建文件版本表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    content BLOB NOT NULL,
                    hash TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建服务器信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            conn.commit()
    
    def save_file_version(self, file_path: str, content: bytes):
        """保存文件版本"""
        file_hash = hashlib.md5(content).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO file_versions (file_path, content, hash) VALUES (?, ?, ?)",
                (file_path, content, file_hash)
            )
            conn.commit()
    
    def get_latest_version(self, file_path: str) -> bytes:
        """获取文件最新版本"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content FROM file_versions WHERE file_path = ? ORDER BY timestamp DESC LIMIT 1",
                (file_path,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_file_history(self, file_path: str) -> list:
        """获取文件历史版本"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT hash, timestamp FROM file_versions WHERE file_path = ? ORDER BY timestamp DESC",
                (file_path,)
            )
            return cursor.fetchall() 