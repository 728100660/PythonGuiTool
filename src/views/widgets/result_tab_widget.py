from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt6.QtCore import Qt
import os
from datetime import datetime
from .result_chart_widget import ResultChartWidget

class ResultTabWidget(QWidget):
    """测试结果标签页"""
    def __init__(self, server_info, results, current_dir, parent=None):
        super().__init__(parent)
        self.server_info = server_info
        self.results = results
        self.current_chart = None
        self.current_dir = current_dir
        
        # 保存结果到文件
        self.save_results()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧文件列表
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        
        # 状态标签
        status_label = QLabel(f"测试状态: {self.results['status']}")
        file_layout.addWidget(status_label)
        
        # 文件树
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("测试结果文件")
        self.populate_file_tree()
        file_layout.addWidget(self.file_tree)
        
        # 右侧图表区域
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        
        # 添加到分割器
        splitter.addWidget(file_widget)
        splitter.addWidget(self.chart_container)
        
        # 设置初始大小
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        
        # 连接信号
        self.file_tree.itemClicked.connect(self.on_file_selected)
    
    def populate_file_tree(self):
        """填充文件树"""
        for result in self.results['results']:
            item = QTreeWidgetItem(self.file_tree)
            item.setText(0, result['file'])
            item.setData(0, Qt.ItemDataRole.UserRole, result)
    
    def on_file_selected(self, item):
        """处理文件选择"""
        result_data = item.data(0, Qt.ItemDataRole.UserRole)
        
        # 清除现有图表
        if self.current_chart:
            self.chart_layout.removeWidget(self.current_chart)
            self.current_chart.deleteLater()
        
        # 创建新图表
        self.current_chart = ResultChartWidget(result_data['content'])
        self.chart_layout.addWidget(self.current_chart)
    
    def save_results(self):
        """保存测试结果到文件"""
        # 确保目录存在
        now = datetime.now()
        result_dir = os.path.join(self.current_dir, 'res', now.strftime('%Y-%m-%d %H-%M-%S'), 
                                str(self.server_info['id']))
        os.makedirs(result_dir, exist_ok=True)
        
        # 保存每个结果文件
        for result in self.results['results']:
            file_path = os.path.join(result_dir, result['file'])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result['content']) 