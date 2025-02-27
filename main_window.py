from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QTreeView, QFileDialog, QLabel,
                           QTextEdit, QDialog, QCheckBox, QScrollArea,
                           QGroupBox, QMessageBox, QTabWidget, QListWidget)
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPainter
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
import os
import re
from file_manager import FileManager
from server_api import ServerAPI
from src.views.widgets.result_tab_widget import ResultTabWidget

class FileViewDialog(QDialog):
    """文件查看对话框"""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"查看文件 - {os.path.basename(file_path)}")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # 显示文件路径
        path_label = QLabel(f"文件路径: {file_path}")
        layout.addWidget(path_label)

        # 文件内容显示区域
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 加载文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_edit.setText(content)
        except Exception as e:
            self.text_edit.setText(f"无法读取文件内容: {str(e)}")

class SubmitDialog(QDialog):
    """提交选择对话框"""
    def __init__(self, all_files, changed_files, servers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择要提交的服务器和文件")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # 服务器选择区域
        server_group = QGroupBox("选择服务器")
        server_layout = QVBoxLayout()
        self.server_checkboxes = {}
        for server in servers:
            cb = QCheckBox(f"{server['name']} ({server['address']})")
            cb.setChecked(True)
            self.server_checkboxes[server['id']] = cb
            server_layout.addWidget(cb)
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # 文件选择区域
        file_group = QGroupBox("选择文件")
        file_layout = QVBoxLayout()
        self.file_checkboxes = {}
        
        # 添加全选按钮
        select_all = QCheckBox("全选")
        file_layout.addWidget(select_all)
        
        # 添加所有文件，变更的文件默认选中
        for file_path in all_files:
            if "res" in file_path.split(os.sep):
                continue
            cb = QCheckBox(file_path)
            cb.setChecked(file_path in changed_files)  # 变更的文件默认选中
            if file_path in changed_files:
                cb.setStyleSheet("color: red;")  # 变更的文件标红
            self.file_checkboxes[file_path] = cb
            file_layout.addWidget(cb)
            
        file_group.setLayout(file_layout)
        
        # 将文件选择区域放入滚动区域
        scroll = QScrollArea()
        scroll.setWidget(file_group)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        # 添加配置按钮
        self.config_btn = QPushButton("测试配置")
        self.config_btn.setMinimumWidth(100)  # 设置最小宽度
        
        # 确认和取消按钮
        self.ok_button = QPushButton("确认")
        self.ok_button.setMinimumWidth(100)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumWidth(100)
        
        # 添加到按钮布局
        buttons_layout.addWidget(self.config_btn)
        buttons_layout.addStretch()  # 添加弹性空间
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        # 重要：将按钮布局添加到主布局
        layout.addLayout(buttons_layout)
        
        # 存储配置
        self.test_config = None
        
        # 连接信号
        self.config_btn.clicked.connect(self.show_config_dialog)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        select_all.stateChanged.connect(
            lambda state: [cb.setChecked(state == Qt.CheckState.Checked.value) 
                         for cb in self.file_checkboxes.values()]
        )
    
    def show_config_dialog(self):
        """显示配置对话框"""
        from src.views.dialogs.config_dialog import ConfigDialog
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.test_config = dialog.get_config()
    
    def get_selected(self):
        """获取选中的服务器和文件"""
        selected_servers = [sid for sid, cb in self.server_checkboxes.items() 
                          if cb.isChecked()]
        selected_files = [path for path, cb in self.file_checkboxes.items() 
                         if cb.isChecked()]
        return selected_servers, selected_files, self.test_config

class TestResultChart(QWidget):
    """测试结果图表显示"""
    def __init__(self, results_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # 创建图表
        chart = QChart()
        chart.setTitle("测试结果统计")
        
        # 创建数据系列
        series = QLineSeries()
        series.setName("中奖次数")
        
        # 解析结果文本
        data_points = self.parse_results(results_text)
        
        # 添加数据点
        max_y = 0
        for i, (total, wins) in enumerate(data_points):
            series.append(i, wins)
            max_y = max(max_y, wins)
        
        # 添加系列到图表
        chart.addSeries(series)
        
        # 创建坐标轴
        axis_x = QValueAxis()
        axis_x.setTitleText("测试次数")
        axis_x.setRange(0, len(data_points) - 1)
        axis_x.setTickCount(min(10, len(data_points)))
        
        axis_y = QValueAxis()
        axis_y.setTitleText("中奖次数")
        axis_y.setRange(0, max_y * 1.1)  # 留出10%的空间
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        # 创建图表视图
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 添加到布局
        layout.addWidget(chart_view)
        
        # 添加原始数据显示
        text_view = QTextEdit()
        text_view.setReadOnly(True)
        text_view.setText(results_text)
        text_view.setMaximumHeight(150)
        layout.addWidget(text_view)
    
    def parse_results(self, text):
        """解析结果文本，返回(总次数, 中奖次数)列表"""
        data_points = []
        # 假设文本格式为：xxx次，中奖数为xxx次
        pattern = r'(\d+)次，中奖数为(\d+)次'
        matches = re.finditer(pattern, text)
        for match in matches:
            total = int(match.group(1))
            wins = int(match.group(2))
            data_points.append((total, wins))
        return data_points

class FileDiffDialog(QDialog):
    """文件对比对话框"""
    def __init__(self, file_path, old_content, new_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"文件对比 - {os.path.basename(file_path)}")
        self.setGeometry(100, 100, 1200, 800)
        
        layout = QVBoxLayout(self)
        
        # 显示文件路径
        path_label = QLabel(f"文件路径: {file_path}")
        layout.addWidget(path_label)
        
        # 对比区域
        diff_layout = QHBoxLayout()
        
        # 旧版本
        old_group = QGroupBox("上一版本")
        old_layout = QVBoxLayout()
        self.old_text = QTextEdit()
        self.old_text.setReadOnly(True)
        old_layout.addWidget(self.old_text)
        old_group.setLayout(old_layout)
        
        # 新版本
        new_group = QGroupBox("当前版本")
        new_layout = QVBoxLayout()
        self.new_text = QTextEdit()
        self.new_text.setReadOnly(True)
        new_layout.addWidget(self.new_text)
        new_group.setLayout(new_layout)
        
        diff_layout.addWidget(old_group)
        diff_layout.addWidget(new_group)
        layout.addLayout(diff_layout)



class MainWindow(QMainWindow):
    def __init__(self, file_manager: FileManager, server_api: ServerAPI):
        super().__init__()
        self.file_manager = file_manager
        self.server_api = server_api
        
        # 初始化模型
        self.server_model = QStandardItemModel()
        self.file_model = QStandardItemModel()
        
        # 存储变更文件列表
        self.changed_files = []
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('服务器配表更新工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板（服务器列表）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.server_label = QLabel("服务器列表")
        self.server_tree = QTreeView()
        self.refresh_servers_btn = QPushButton("刷新服务器列表")
        
        left_layout.addWidget(self.server_label)
        left_layout.addWidget(self.server_tree)
        left_layout.addWidget(self.refresh_servers_btn)
        
        # 中间面板（文件树和变更文件）
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        
        # 工程目录操作按钮
        dir_buttons_layout = QHBoxLayout()
        self.select_dir_btn = QPushButton("选择工程目录")
        self.refresh_dir_btn = QPushButton("刷新工程目录")
        self.current_dir_label = QLabel("当前目录: 未选择")
        dir_buttons_layout.addWidget(self.select_dir_btn)
        dir_buttons_layout.addWidget(self.refresh_dir_btn)
        dir_buttons_layout.addWidget(self.current_dir_label)
        middle_layout.addLayout(dir_buttons_layout)
        
        # 变更文件使用树形视图替代列表
        changed_group = QGroupBox("变更文件")
        changed_layout = QVBoxLayout()
        self.changed_tree = QTreeView()
        self.changed_model = QStandardItemModel()
        self.changed_tree.setModel(self.changed_model)
        changed_layout.addWidget(self.changed_tree)
        changed_group.setLayout(changed_layout)
        
        # 文件树和变更文件的分割显示
        files_layout = QHBoxLayout()
        
        # 文件树部分
        tree_group = QGroupBox("文件树")
        tree_layout = QVBoxLayout()
        self.file_tree = QTreeView()
        tree_layout.addWidget(self.file_tree)
        tree_group.setLayout(tree_layout)
        
        files_layout.addWidget(tree_group)
        files_layout.addWidget(changed_group)
        middle_layout.addLayout(files_layout)
        
        # 提交按钮
        self.submit_btn = QPushButton("提交更新")
        middle_layout.addWidget(self.submit_btn)
        
        # 右侧面板（测试结果）
        self.result_tabs = QTabWidget()
        self.result_tabs.setTabsClosable(True)
        self.result_tabs.tabCloseRequested.connect(self.close_result_tab)
        
        # 添加到主布局
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(middle_panel, 4)
        main_layout.addWidget(self.result_tabs, 8)
        
        # 设置模型
        self.server_tree.setModel(self.server_model)
        self.file_tree.setModel(self.file_model)
        
        # 初始化服务器列表
        self.refresh_servers()
        
        # 连接信号
        self.connect_signals()
    
    def connect_signals(self):
        """连接信号和槽"""
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.refresh_dir_btn.clicked.connect(self.refresh_directory)
        self.refresh_servers_btn.clicked.connect(self.refresh_servers)
        self.submit_btn.clicked.connect(self.submit_changes)
        
        # 修改文件树的信号连接
        self.file_tree.clicked.connect(self.on_file_selected)
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
        self.changed_tree.doubleClicked.connect(self.on_changed_file_double_clicked)
        
        # 添加服务器选择响应
        self.server_tree.clicked.connect(self.on_server_selected)


    def select_directory(self):
        """选择工程目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择工程目录")
        if dir_path:
            self.file_manager.set_project_directory(dir_path)
            self.current_dir_label.setText(f"当前目录: {dir_path}")
            
            # 更新文件树
            self.update_file_tree()
            
            # 检测并显示变更文件
            self.changed_files = self.file_manager.get_changed_files()
            self.update_changed_tree()
    
    def refresh_directory(self):
        """刷新工程目录"""
        if self.file_manager.project_directory:
            self.update_file_tree()
            self.update_changed_tree()
    
    def update_file_tree(self):
        """更新文件树"""
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(['文件'])
        
        if not self.file_manager.project_directory:
            return
            
        root = self.file_model.invisibleRootItem()
        file_tree = self.file_manager.get_file_tree()
        self._build_tree(root, file_tree)
        
        # 展开根节点
        self.file_tree.expandToDepth(0)
    
    def _build_tree(self, parent_item: QStandardItem, tree_dict: dict):
        """递归构建文件树"""
        for name, value in tree_dict.items():
            item = QStandardItem(name)
            parent_item.appendRow(item)
            
            if isinstance(value, dict):  # 如果是目录
                self._build_tree(item, value)
    
    def on_server_selected(self, index: QModelIndex):
        """处理服务器选择事件"""
        server_id = index.data(Qt.ItemDataRole.UserRole)
        server_name = index.data(Qt.ItemDataRole.DisplayRole)
        print(f"选择了服务器: {server_name} (ID: {server_id})")
    
    def on_file_selected(self, index: QModelIndex):
        """处理文件选择事件"""
        path = []
        current = index
        while current.isValid():
            path.insert(0, current.data())
            current = current.parent()
        
        file_path = os.path.join(self.file_manager.project_directory, *path)
        
        # 如果选中的是文件，同步选中变更文件树中的对应项
        if os.path.isfile(file_path) and file_path in self.changed_files:
            self.select_changed_file(file_path)
    
    def on_file_double_clicked(self, index: QModelIndex):
        """处理文件双击事件"""
        path = []
        current = index
        while current.isValid():
            path.insert(0, current.data())
            current = current.parent()
        
        file_path = os.path.join(self.file_manager.project_directory, *path)
        
        if os.path.isfile(file_path):
            self.show_file_diff(file_path)
    
    def on_changed_file_double_clicked(self, index: QModelIndex):
        """处理变更文件双击事件"""
        path = []
        current = index
        while current.isValid():
            path.insert(0, current.data())
            current = current.parent()
        
        file_path = os.path.join(self.file_manager.project_directory, *path)
        
        if os.path.isfile(file_path):
            self.show_file_diff(file_path)

    def show_file_diff(self, file_path: str):
        """显示文件差异 TODO """
    
    def select_changed_file(self, file_path: str):
        """在变更文件树中选中指定文件"""
        rel_path = os.path.relpath(file_path, self.file_manager.project_directory)
        parts = rel_path.split(os.sep)
        
        def find_item(model, parts, parent=None):
            if not parts:
                return None
            parent = parent or model.invisibleRootItem()
            for row in range(parent.rowCount()):
                item = parent.child(row)
                if item.text() == parts[0]:
                    if len(parts) == 1:
                        return item.index()
                    return find_item(model, parts[1:], item)
            return None
        
        index = find_item(self.changed_model, parts)
        if index:
            self.changed_tree.setCurrentIndex(index)
    
    def refresh_servers(self):
        """刷新服务器列表"""
        self.server_model.clear()
        self.server_model.setHorizontalHeaderLabels(['服务器列表'])
        
        servers = self.server_api.get_server_list()
        for server in servers:
            item = QStandardItem(f"{server['name']} ({server['address']})")
            item.setData(server['id'], Qt.ItemDataRole.UserRole)  # 存储服务器ID
            self.server_model.appendRow(item)
    
    def submit_changes(self):
        """提交更新"""
        if not self.file_manager.project_directory:
            QMessageBox.warning(self, "警告", "请先选择工程目录")
            return
        
        # 获取所有文件列表
        all_files = self.file_manager.get_all_files()
        
        # 打开选择对话框
        dialog = SubmitDialog(all_files, self.changed_files, 
                            self.server_api.get_server_list(), self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_servers, selected_files, test_config = dialog.get_selected()
            
            if not test_config:
                QMessageBox.warning(self, "警告", "请先配置测试参数")
                return

            # 更新保存的文件版本
            for file in selected_files:
                self.file_manager.save_current_version(file)
            
            # 对每个选中的服务器进行更新
            for server_id in selected_servers:
                success = self.server_api.update_config(
                    server_id, selected_files, test_config)
                if success:
                    # 获取测试结果并添加新标签页
                    test_results = self.server_api.get_test_results(server_id)
                    self.add_result_tab(server_id, test_results)
                else:
                    QMessageBox.warning(self, "错误", 
                                      f"服务器 {server_id} 更新失败")
    
    def update_changed_tree(self):
        """更新变更文件树"""
        self.changed_model.clear()
        self.changed_model.setHorizontalHeaderLabels(['变更文件'])
        
        if not self.file_manager.project_directory:
            return
            
        # 获取变更文件列表
        self.changed_files = self.file_manager.get_changed_files()
        
        # 构建树形结构
        root = self.changed_model.invisibleRootItem()
        tree_dict = {}
        
        # 将文件路径组织成树形结构
        for file_path in self.changed_files:
            rel_path = os.path.relpath(file_path, self.file_manager.project_directory)
            parts = rel_path.split(os.sep)
            current = tree_dict
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = None
        
        # 构建树形视图
        self._build_tree(root, tree_dict)
        self.changed_tree.expandAll()
    
    def add_result_tab(self, server_id: int, results: dict):
        """添加测试结果标签页"""
        # 获取服务器信息
        server_info = next(s for s in self.server_api.get_server_list() 
                         if s['id'] == server_id)
        
        # 创建结果标签页
        result_tab = ResultTabWidget(server_info, results, self.file_manager.project_directory)
        
        # 添加新标签页
        tab_name = f"{server_info['name']}"
        self.result_tabs.addTab(result_tab, tab_name)
        self.result_tabs.setCurrentIndex(self.result_tabs.count() - 1)
    
    def close_result_tab(self, index: int):
        """关闭结果标签页"""
        self.result_tabs.removeTab(index)
    
    def view_result_file(self, file_path: str):
        """查看结果文件"""
        dialog = FileViewDialog(file_path, self)
        dialog.exec() 