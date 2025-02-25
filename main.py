import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from database import Database
from file_manager import FileManager
from server_api import ServerAPI

def main():
    """主程序入口"""
    # 初始化应用
    app = QApplication(sys.argv)
    
    # 初始化各个模块
    db = Database()
    file_manager = FileManager(db)
    server_api = ServerAPI()
    
    # 创建主窗口
    window = MainWindow(file_manager, server_api)
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 