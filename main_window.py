from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QTreeView, QFileDialog, QLabel,
                           QTextEdit, QDialog, QCheckBox, QScrollArea,
                           QGroupBox, QMessageBox, QTabWidget, QListWidget,
                           QSplitter, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPainter
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
import os
import re
from file_manager import FileManager
from server_api import ServerAPI
from src.views.widgets.result_tab_widget import ResultTabWidget
from src.views.dialogs.config_dialog import ConfigDialog
import json

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
        
        # 显示内容并高亮差异
        self.show_diff(old_content, new_content)
    
    def show_diff(self, old_content, new_content):
        """显示并高亮差异"""
        import difflib
        
        # 将二进制内容转换为文本
        try:
            old_text = old_content.decode('utf-8') if old_content else ""
            new_text = new_content.decode('utf-8') if new_content else ""
        except UnicodeDecodeError:
            self.old_text.setText("二进制文件")
            self.new_text.setText("二进制文件")
            return
            
        # 获取差异
        differ = difflib.Differ()
        diff = list(differ.compare(old_text.splitlines(), new_text.splitlines()))
        
        # 显示旧版本，标记删除的行
        old_html = []
        for line in diff:
            if line.startswith('  ') or line.startswith('- '):
                text = line[2:]
                if line.startswith('- '):
                    text = f'<span style="background-color: #ffcdd2;">{text}</span>'
                old_html.append(text)
        self.old_text.setHtml('<br>'.join(old_html))
        
        # 显示新版本，标记添加的行
        new_html = []
        for line in diff:
            if line.startswith('  ') or line.startswith('+ '):
                text = line[2:]
                if line.startswith('+ '):
                    text = f'<span style="background-color: #c8e6c9;">{text}</span>'
                new_html.append(text)
        self.new_text.setHtml('<br>'.join(new_html))

class ConfigConfirmDialog(QDialog):
    """配置确认对话框"""
    def __init__(self, config_type, config_data, server_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("确认配置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 服务器信息
        server_label = QLabel(f"目标服务器: {server_name}")
        server_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(server_label)
        
        # 配置类型
        type_label = QLabel(f"配置类型: {config_type}")
        type_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(type_label)
        
        # 配置内容
        content = QTextEdit()
        content.setReadOnly(True)
        content.setMaximumHeight(200)
        content.setText(json.dumps(config_data, indent=2, ensure_ascii=False))
        layout.addWidget(content)
        
        # 不再提示选项
        self.dont_show = QCheckBox("本次运行期间不再提示")
        layout.addWidget(self.dont_show)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确认")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

class MainWindow(QMainWindow):
    def __init__(self, file_manager: FileManager, server_api: ServerAPI):
        super().__init__()
        self.file_manager = file_manager
        self.server_api = server_api
        self.skip_config_confirm = False  # 添加标志
        
        # 初始化模型
        self.server_model = QStandardItemModel()
        self.file_model = QStandardItemModel()
        
        # 存储变更文件列表
        self.changed_files = []
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('服务器配表更新工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建水平分割器
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 中间面板 - 配置和文件列表
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        
        # 目录选择区域
        dir_area = QWidget()
        dir_layout = QVBoxLayout(dir_area)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        
        # 第一行：工程目录
        project_dir_layout = QHBoxLayout()
        self.select_dir_btn = QPushButton("选择工程目录")
        self.refresh_dir_btn = QPushButton("刷新工程目录")
        self.current_dir_label = QLabel("当前工程目录: 未选择")
        project_dir_layout.addWidget(self.select_dir_btn)
        project_dir_layout.addWidget(self.refresh_dir_btn)
        project_dir_layout.addWidget(self.current_dir_label)
        project_dir_layout.addStretch()
        dir_layout.addLayout(project_dir_layout)
        
        # 第二行：结果存储目录
        result_dir_layout = QHBoxLayout()
        self.res_dir_btn = QPushButton("选择结果存储目录")
        self.current_res_dir_label = QLabel("当前结果目录: 未选择")
        result_dir_layout.addWidget(self.res_dir_btn)
        result_dir_layout.addWidget(self.current_res_dir_label)
        result_dir_layout.addStretch()
        dir_layout.addLayout(result_dir_layout)

        middle_layout.addWidget(dir_area)

        # 在文件树上方添加配置区域
        config_group = QGroupBox("测试配置")
        self.config_group = config_group
        config_layout = QVBoxLayout()
        
        # 配置类型选择
        config_type_layout = QHBoxLayout()
        self.config_type_group = QButtonGroup(self)
        for config_type in ["task_info", "initial_info", "old_game"]:
            radio = QRadioButton(config_type)
            self.config_type_group.addButton(radio)
            config_type_layout.addWidget(radio)
        config_layout.addLayout(config_type_layout)
        
        # 配置按钮
        config_btn_layout = QHBoxLayout()
        self.edit_config_btn = QPushButton("编辑配置")
        config_btn_layout.addWidget(self.edit_config_btn)
        config_layout.addLayout(config_btn_layout)

        # 服务器列表
        server_label = QLabel("服务器列表")
        server_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        config_layout.addWidget(server_label)

        config_group.setLayout(config_layout)
        middle_layout.addWidget(config_group)

        # 服务器按钮组
        self.server_buttons = QButtonGroup(self)
        self.refresh_servers()  # 初始化服务器列表
        
        # 创建垂直分割器用于文件树和变更文件树
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 文件树
        file_tree_widget = QWidget()
        file_tree_layout = QVBoxLayout(file_tree_widget)
        file_tree_layout.setContentsMargins(0, 0, 0, 0)
        file_tree_label = QLabel("文件列表")
        file_tree_layout.addWidget(file_tree_label)
        self.file_tree = QTreeView()
        self.file_model = QStandardItemModel()
        self.file_model.setHorizontalHeaderLabels(['文件列表'])
        self.file_tree.setModel(self.file_model)
        file_tree_layout.addWidget(self.file_tree)
        v_splitter.addWidget(file_tree_widget)
        
        # 变更文件树
        changed_tree_widget = QWidget()
        changed_tree_layout = QVBoxLayout(changed_tree_widget)
        changed_tree_layout.setContentsMargins(0, 0, 0, 0)
        changed_tree_label = QLabel("变更文件")
        changed_tree_layout.addWidget(changed_tree_label)
        self.changed_tree = QTreeView()
        self.changed_model = QStandardItemModel()
        self.changed_model.setHorizontalHeaderLabels(['变更文件'])
        self.changed_tree.setModel(self.changed_model)
        changed_tree_layout.addWidget(self.changed_tree)
        v_splitter.addWidget(changed_tree_widget)
        
        middle_layout.addWidget(v_splitter)
        
        # 提交按钮
        self.submit_btn = QPushButton("提交更新")
        middle_layout.addWidget(self.submit_btn)
        
        # 将中间面板添加到水平分割器
        h_splitter.addWidget(middle_panel)
        
        # 右侧面板 - 结果标签页
        self.result_tabs = QTabWidget()
        self.result_tabs.setTabsClosable(True)
        self.result_tabs.tabCloseRequested.connect(self.close_result_tab)
        h_splitter.addWidget(self.result_tabs)
        
        # 设置分割器的初始大小比例
        h_splitter.setSizes([200, 400, 600])  # 左侧、中间、右侧的初始宽度
        
        # 将水平分割器添加到主布局
        main_layout.addWidget(h_splitter)
        
        # 连接信号
        self.connect_signals()
        
        # 添加新的信号连接
        self.edit_config_btn.clicked.connect(self.edit_config)
        
        # 加载保存的配置
        self.load_saved_configs()
    
    def connect_signals(self):
        """连接信号和槽"""
        self.select_dir_btn.clicked.connect(self.select_project_directory)
        self.refresh_dir_btn.clicked.connect(self.refresh_directory)
        self.res_dir_btn.clicked.connect(self.select_result_directory)
        # self.refresh_servers_btn.clicked.connect(self.refresh_servers)
        self.submit_btn.clicked.connect(self.submit_changes)
        self.server_buttons.buttonClicked.connect(self.on_server_selected)
        
        # 修改文件树的信号连接
        self.file_tree.clicked.connect(self.on_file_selected)
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
        self.changed_tree.doubleClicked.connect(self.on_changed_file_double_clicked)
    
    def select_project_directory(self):
        """选择工程目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择工程目录")
        if dir_path:
            self.file_manager.set_project_directory(dir_path)
            self.current_dir_label.setText(f"当前工程目录: {dir_path}")
            
            # 更新默认结果目录显示
            default_res_dir = self.file_manager.get_result_directory()
            self.current_res_dir_label.setText(
                f"当前结果目录: {default_res_dir} (默认)"
            )
            
            # 更新文件树
            self.update_file_tree()
            
            # 检测并显示变更文件
            # self.changed_files = self.file_manager.get_changed_files()
            self.update_changed_tree()

    def select_result_directory(self):
        """选择结果存储目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择结果存储目录")
        if dir_path:
            self.file_manager.set_result_directory(dir_path)
            self.current_res_dir_label.setText(f"当前结果目录: {dir_path}")

    def refresh_directory(self):
        """刷新工程目录"""
        if self.file_manager.project_directory:
            # 更新文件树
            self.update_file_tree()
            
            # 检测并显示变更文件
            # self.changed_files = self.file_manager.get_changed_files()
            self.update_changed_tree()
    
    def update_file_tree(self):
        """更新文件树"""
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(['文件列表'])
        
        if not self.file_manager.project_directory:
            return
        
        # 获取文件树结构
        tree_dict = self.file_manager.get_file_tree()
        root = self.file_model.invisibleRootItem()
        
        # 构建树形视图
        self._build_tree(root, tree_dict)
        self.file_tree.expandAll()

    def _build_tree(self, parent_item, tree_dict):
        """递归构建树形结构"""
        for key, value in sorted(tree_dict.items()):
            item = QStandardItem(key)
            parent_item.appendRow(item)
            if isinstance(value, dict):  # 如果是目录
                self._build_tree(item, value)
    
    def on_server_selected(self, button):
        """处理服务器选择事件"""
        server_id = button.property('server_id')
        self.file_manager.database.save_selected_server(server_id)
    
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
        """显示文件差异"""
        try:
            with open(file_path, 'rb') as f:
                new_content = f.read()
            old_content = self.file_manager.database.get_latest_version(file_path)
            
            dialog = FileDiffDialog(file_path, old_content, new_content, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件: {str(e)}")
    
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
        # 清除现有按钮
        for button in self.server_buttons.buttons():
            self.server_buttons.removeButton(button)
            button.deleteLater()
        
        # 获取上次选中的服务器ID
        last_selected = self.file_manager.database.get_selected_server()
        
        # 添加新的服务器按钮
        for server in self.server_api.get_server_list():
            radio = QRadioButton(f"{server['name']} ({server['address']})")
            radio.setProperty('server_id', server['id'])
            self.server_buttons.addButton(radio)
            self.config_group.layout().addWidget(radio)
            
            # 如果是上次选中的服务器，设置为选中状态
            if last_selected and server['id'] == last_selected:
                radio.setChecked(True)
        
        # 连接信号
        self.server_buttons.buttonClicked.connect(self.on_server_selected)

    def submit_changes(self):
        """提交更新"""
        if not self.file_manager.project_directory:
            QMessageBox.warning(self, "警告", "请先选择工程目录")
            return
        
        # 获取选中的配置类型
        config_type = self.get_selected_config_type()
        if not config_type:
            QMessageBox.warning(self, "警告", "请选择配置类型")
            return
        
        # 获取配置
        configs = self.file_manager.database.get_selected_configs()
        if not configs or config_type not in configs:
            QMessageBox.warning(self, "警告", "请先设置配置")
            return

        # 获取选中的服务器
        selected_button = self.server_buttons.checkedButton()
        if not selected_button:
            QMessageBox.warning(self, "警告", "请选择服务器")
            return

        server_id = selected_button.property('server_id')
        server = next(s for s in self.server_api.get_server_list() if s['id'] == server_id)
        
        # 显示配置确认对话框
        if not self.skip_config_confirm:
            dialog = ConfigConfirmDialog(config_type, configs[config_type],
                                         self.server_api.get_server_name(server_id), self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            self.skip_config_confirm = dialog.dont_show.isChecked()
        
        # 获取所有变更文件
        changed_files = self.file_manager.get_changed_files()
        
        # 断开之前的信号连接
        try:
            self.server_api.result_listener.result_updated.disconnect()
        except:
            pass  # 如果没有连接，忽略错误
        
        # 创建结果标签页
        initial_results = {"status": "starting", "results": []}
        self.add_result_tab(server_id, initial_results, configs[config_type])
        
        # 连接结果更新信号
        self.server_api.result_listener.result_updated.connect(
            lambda results: self.update_result_tab(server_id, results)
        )
        
        # 启动测试
        test_config = {config_type: configs[config_type]}
        success = self.server_api.update_config(
            server_id, changed_files, test_config,
            self.file_manager.project_directory
        )
        
        if not success:
            QMessageBox.warning(self, "错误", f"服务器 {server['name']} 更新失败")
    
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
    
    def add_result_tab(self, server_id: int, results: dict, config):
        """添加测试结果标签页"""
        # 获取服务器信息
        server_info = next(s for s in self.server_api.get_server_list() 
                          if s['id'] == server_id)
        
        # 创建结果标签页，使用结果存储目录
        result_tab = ResultTabWidget(
            server_info, 
            results, 
            self.file_manager.get_result_directory(),
            server_api=self.server_api,
            config=config
        )
        
        # 添加新标签页
        tab_name = f"{server_info['name']}"
        self.result_tabs.addTab(result_tab, tab_name)
        self.result_tabs.setCurrentIndex(self.result_tabs.count() - 1)
    
    def close_result_tab(self, index: int):
        """关闭结果标签页"""
        # 获取要关闭的标签页
        tab = self.result_tabs.widget(index)
        if isinstance(tab, ResultTabWidget):
            # 调用关闭方法
            tab.close()
        # 移除标签页
        self.result_tabs.removeTab(index)
    
    def view_result_file(self, file_path: str):
        """查看结果文件"""
        dialog = FileViewDialog(file_path, self)
        dialog.exec()
    
    def update_result_tab(self, server_id: int, results: dict):
        """更新结果标签页"""
        # 查找对应的标签页
        for i in range(self.result_tabs.count()):
            tab = self.result_tabs.widget(i)
            if isinstance(tab, ResultTabWidget) and tab.server_info['id'] == server_id:
                tab.update_results(results)
                break 

    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        self.file_manager.stop_save_thread()
        super().closeEvent(event)

    def load_saved_configs(self):
        """加载保存的配置"""
        configs = self.file_manager.database.get_selected_configs()
        if configs:
            # 获取上次选中的配置类型
            last_selected = self.file_manager.database.get_selected_config_type()
            # 找到对应的配置类型并选中
            for button in self.config_type_group.buttons():
                if (last_selected and button.text() == last_selected) or \
                   (not last_selected and button.text() in configs):
                    button.setChecked(True)
                    break

    def edit_config(self):
        """编辑配置"""
        config_type = self.get_selected_config_type()
        if not config_type:
            QMessageBox.warning(self, "警告", "请选择配置类型")
            return
        
        # 获取已保存的配置
        saved_configs = self.file_manager.database.get_selected_configs()
        dialog = ConfigDialog(self, last_config=saved_configs, config_type=config_type)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            # 保存到数据库
            self.file_manager.database.save_config(config_type, config[config_type], True)

    def get_selected_config_type(self):
        """获取选中的配置类型"""
        button = self.config_type_group.checkedButton()
        return button.text() if button else None
