import sqlite3
import os
import hashlib
from datetime import datetime
import json

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
            
            # 创建配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_type TEXT NOT NULL,  -- 'task_info', 'initial_info', 'old_game'
                    config_data TEXT NOT NULL,
                    is_selected INTEGER DEFAULT 0,  -- 是否被选中
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建用户偏好表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            conn.commit()
    def save_selected_config_type(self, config_type: str):
        """保存用户选中的配置类型"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                ("selected_config_type", config_type)
            )
            conn.commit()

    def get_selected_config_type(self) -> str:
        """获取用户上次选中的配置类型"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM user_preferences WHERE key = ?",
                ("selected_config_type",)
            )
            result = cursor.fetchone()
            return result[0] if result else None
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

    def save_config(self, config_type: str, config_data: dict, is_selected: bool = False):
        """保存测试配置，无则新增，有则更新"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在该类型的配置
            cursor.execute(
                "SELECT id FROM test_configs WHERE config_type = ?",
                (config_type,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有配置
                cursor.execute(
                    "UPDATE test_configs SET config_data = ?, is_selected = ?, timestamp = CURRENT_TIMESTAMP WHERE config_type = ?",
                    (json.dumps(config_data), int(is_selected), config_type)
                )
            else:
                # 插入新配置
                cursor.execute(
                    "INSERT INTO test_configs (config_type, config_data, is_selected) VALUES (?, ?, ?)",
                    (config_type, json.dumps(config_data), int(is_selected))
                )
            
            if is_selected:
                # 取消其他同类型配置的选中状态
                cursor.execute(
                    "UPDATE test_configs SET is_selected = 0 WHERE config_type = ? AND id != ?",
                    (config_type, cursor.lastrowid if not existing else existing[0])
                )
            conn.commit()

    def get_selected_configs(self) -> dict:
        """获取当前选中的配置"""
        configs = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT config_type, config_data FROM test_configs WHERE is_selected = 1"
            )
            for config_type, config_data in cursor.fetchall():
                configs[config_type] = json.loads(config_data)
        return configs

    def save_selected_server(self, server_id: int):
        """保存用户选中的服务器ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                ("selected_server", str(server_id))
            )
            conn.commit()

    def get_selected_server(self) -> int:
        """获取用户上次选中的服务器ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM user_preferences WHERE key = ?",
                ("selected_server",)
            )
            result = cursor.fetchone()
            return int(result[0]) if result else None