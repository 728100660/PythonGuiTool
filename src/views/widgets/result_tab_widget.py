from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTreeWidget, QTreeWidgetItem, QSplitter, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt
from simu_data_get import SimuData
import os
from datetime import datetime
from .result_chart_widget import ResultChartWidget
from simu_data_get import SimuData

class ResultTabWidget(QWidget):
    """测试结果标签页"""
    def __init__(self, server_info, results, res_dir, parent=None,
                 server_api=None, config=None):
        super().__init__(parent)
        self.server_info = server_info
        self.results = results
        self.current_chart = None
        self.current_table = None
        self.res_dir = res_dir
        self.start_time = datetime.now()
        self.server_api = server_api
        self.config = config
        
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
        self.status_label = QLabel(f"测试状态: {self.results['status']}")
        file_layout.addWidget(self.status_label)
        
        # 文件树
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("测试结果文件")
        self.populate_file_tree()
        file_layout.addWidget(self.file_tree)
        
        # 右侧区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 图表区域
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        right_layout.addWidget(self.chart_container)
        
        # 表格区域
        self.table_view = QTextEdit()
        self.table_view.setReadOnly(True)
        self.table_view.setFont(QFont("Courier New", 10))
        right_layout.addWidget(self.table_view)
        
        # 添加停止按钮
        self.stop_btn = QPushButton("停止测试")
        self.stop_btn.clicked.connect(self.stop_test)
        right_layout.addWidget(self.stop_btn)
        
        # 添加到分割器
        splitter.addWidget(file_widget)
        splitter.addWidget(right_widget)
        
        # 设置初始大小
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        
        # 连接信号
        self.file_tree.itemClicked.connect(self.on_file_selected)
    
    def populate_file_tree(self):
        """填充文件树"""
        for result in self.results['results']:
            if result.get('type') == 'folder':
                # 创建文件夹节点
                folder_item = QTreeWidgetItem(self.file_tree)
                folder_item.setText(0, result['name'])
                
                # 添加子项
                for child in result['children']:
                    child_item = QTreeWidgetItem(folder_item)
                    child_item.setText(0, child['file'])
                    child_item.setData(0, Qt.ItemDataRole.UserRole, child)
            else:
                # 直接添加文件
                item = QTreeWidgetItem(self.file_tree)
                item.setText(0, result['file'])
                item.setData(0, Qt.ItemDataRole.UserRole, result)
        
        # 展开所有项
        self.file_tree.expandAll()
    
    def on_file_selected(self, item):
        """处理文件选择"""
        result_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not result_data:  # 如果是文件夹节点，不显示图表
            return
        
        # 清除现有图表
        if self.current_chart:
            self.chart_layout.removeWidget(self.current_chart)
            self.current_chart.deleteLater()
        
        # 创建新图表
        self.current_chart = ResultChartWidget(
            result_data['content'],
            series_data=result_data.get('series_data')
        )
        self.chart_layout.addWidget(self.current_chart)
        
        # 显示表格数据
        if 'data_info' in result_data:
            table_content = SimuData.print_lab(result_data['data_info'])
            self.table_view.setText(table_content)
        else:
            # 显示普通文本内容
            self.table_view.setText(result_data['content'])
        self.file_tree.setCurrentItem(item)

    def save_results(self):
        """保存测试结果到文件"""
        # 确保目录存在
        result_dir = os.path.join(
            self.res_dir,  # 这里current_dir已经是结果存储目录
            'res',
            self.start_time.strftime('%Y-%m-%d %H-%M-%S'),
            str(self.server_info['id'])
        )
        os.makedirs(result_dir, exist_ok=True)
        
        # 保存每个结果文件
        for result in self.results['results']:
            if result.get('type') == 'folder':
                # 创建文件夹
                folder_path = os.path.join(result_dir, result['name'])
                os.makedirs(folder_path, exist_ok=True)
                
                # 保存子文件
                for child in result['children']:
                    file_path = os.path.join(folder_path, child['file'])
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # 保存表格格式的数据
                        if 'series_data' in child:
                            series = child['series_data']
                            f.write(f"次数\t{series['name']}\n")
                            for x, y in series['data']:
                                f.write(f"{x}\t{y}\n")
                        else:
                            f.write(child['content'])
            else:
                file_path = os.path.join(result_dir, result['file'])
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
    
    def update_results(self, results: dict):
        """更新测试结果"""
        # 保存当前选中的文件名
        current_item = self.file_tree.currentItem()
        current_file_name = current_item.text(0) if current_item else None
        
        self.results = results
        
        # 更新状态标签
        self.status_label.setText(f"测试状态: {results['status']}")
        
        # 更新文件树
        self.file_tree.clear()
        self.populate_file_tree()
        # # 如果当前有选中的图表，更新它
        # if self.current_chart and self.file_tree.currentItem():
        #     self.on_file_selected(self.file_tree.currentItem())
        # 如果之前有选中的文件，找到并重新选中它
        if current_file_name:
            items = self.file_tree.findItems(current_file_name, Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive)
            if items:
                self.file_tree.setCurrentItem(items[0])
                self.on_file_selected(items[0])
        
        self.save_results()

    def stop_test(self):
        """停止测试"""
        if self.server_api.stop_test(
                self.server_info['id'], self.config.get("gameId")):
            self.status_label.setText("测试状态: stopped")
            self.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        """关闭事件"""
        # 调用停止接口
        self.server_api.stop_test(self.server_info['id'], self.config.get("gameId"))
        super().closeEvent(event)