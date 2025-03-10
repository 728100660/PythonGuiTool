from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QGroupBox, QFormLayout, QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt
import json

class ConfigDialog(QDialog):
    def __init__(self, parent=None, last_config=None, config_type=None):
        super().__init__(parent)
        self.setWindowTitle("测试配置")
        self.setGeometry(100, 100, 600, 800)
        self.last_configs = last_config
        self.config_type = config_type
        self.default_config = self.get_default_config()
        self.config_inputs = self.create_input_group(self.default_config)

        if last_config:
            self.task_info = last_config.get("task_info")
            self.initial_info = last_config.get("initial_info")
            self.old_game = last_config.get("old_game")
        self.init_ui()

    def get_default_config(self):
        default_config = self.last_configs.get(self.config_type)
        if not default_config:
            default_configs = dict(
                task_info={
                    'betMoney': 2000000,
                    'betType': 0,
                    'gameActive': 1,
                    'gameId': 1,
                    'initLevel': 650,
                    'initMoney': 10000000000000000000,
                    'threadNum': 1,
                    'times': 10000,
                },
                initial_info={
                    'betMoney': 1000000000,
                    'betType': 0,
                    'gameActive': 1,
                    'gameId': 162,
                    'brokenInitialIndex': 60,
                    'ex': 0.9,
                    'unlockFunction': True,
                    # 'group':30,
                    # 'chooseIndex':0,
                    'initVipLevel': 1,
                    'initLevel': 100,
                    'initMoney': 10000000000000000000,
                    'threadNum': 8,
                    'times': 50000000,
                },
                old_game={
                    'betMoney': 10000,
                    'betTypeEnum': 'REGULAR',
                    'gameId': 1,
                    'gameActive': 1,
                    'initMoney': 10000000000,
                    'level': 200,
                    'parameter': 2,
                    'run': 10000000,
                    'thread': 1,
                }
            )
            default_config = default_configs.get(self.config_type)
        return default_config
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()

        # 创建配置编辑页面
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QFormLayout(scroll_content)
        
        # 添加现有配置项
        for label, input_field in self.config_inputs.items():
            self.form_layout.addRow(label, input_field)
        
        scroll.setWidget(scroll_content)
        config_layout.addWidget(scroll)
        
        # 添加新配置项的区域
        add_config_group = QGroupBox("添加新配置项")
        add_layout = QHBoxLayout()
        self.new_key = QLineEdit()
        self.new_key.setPlaceholderText("配置项名称")
        self.new_value = QLineEdit()
        self.new_value.setPlaceholderText("配置项值")
        add_btn = QPushButton("+")
        add_btn.clicked.connect(self.add_config_item)
        
        add_layout.addWidget(self.new_key)
        add_layout.addWidget(self.new_value)
        add_layout.addWidget(add_btn)
        add_config_group.setLayout(add_layout)
        config_layout.addWidget(add_config_group)
        
        tab_widget.addTab(config_tab, self.config_type)
        layout.addWidget(tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 添加确定/取消按钮
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_config_item(self):
        """添加新的配置项"""
        key = self.new_key.text().strip()
        value = self.new_value.text().strip()
        
        if not key:
            QMessageBox.warning(self, "警告", "请输入配置项名称")
            return
            
        if key in self.config_inputs:
            QMessageBox.warning(self, "警告", "配置项已存在")
            return
        
        # 创建新的输入字段
        input_field = QLineEdit()
        input_field.setText(value)
        
        # 创建删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setMaximumWidth(60)
        delete_btn.clicked.connect(lambda: self.delete_config_item(key))
        
        # 创建水平布局来容纳输入字段和删除按钮
        input_layout = QHBoxLayout()
        input_layout.addWidget(input_field)
        input_layout.addWidget(delete_btn)
        
        # 将新配置项添加到表单
        self.form_layout.addRow(key, input_layout)
        self.config_inputs[key] = input_field
        
        # 清空输入框
        self.new_key.clear()
        self.new_value.clear()
    
    def delete_config_item(self, key):
        """删除配置项"""
        # 获取要删除的行索引
        for i in range(self.form_layout.rowCount()):
            label_item = self.form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label_item and label_item.widget().text() == key:
                # 删除表单中的行
                self.form_layout.removeRow(i)
                # 从配置输入字典中删除
                del self.config_inputs[key]
                break

    def create_input_group(self, data):
        """创建输入字段组"""
        inputs = {}
        for key, value in data.items():
            input_field = QLineEdit()
            if isinstance(value, bool):
                input_field.setText(str(value).lower())
            else:
                input_field.setText(str(value))
            
            # 创建删除按钮
            delete_btn = QPushButton("删除")
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked, k=key: self.delete_config_item(k))
            
            # 创建水平布局来容纳输入字段和删除按钮
            input_layout = QHBoxLayout()
            input_layout.addWidget(input_field)
            input_layout.addWidget(delete_btn)
            
            # 创建一个容器widget来承载水平布局
            container = QWidget()
            container.setLayout(input_layout)
            
            inputs[key] = container
        return inputs

    def get_config(self):
        """获取配置数据"""
        try:
            config_type_input = {}
            for k, v in self.config_inputs.items():
                # 获取水平布局中的第一个控件（QLineEdit）
                layout = v.layout()
                if layout:
                    line_edit = layout.itemAt(0).widget()
                    if line_edit:
                        config_type_input[k] = self.parse_value(line_edit.text())
                else:
                    config_type_input[k] = v.text()

            return {
                self.config_type: config_type_input
            }
        except ValueError as e:
            QMessageBox.warning(self, "输入错误", str(e))
            return None
    
    def parse_value(self, text):
        """解析输入值"""
        text = text.strip()
        if text.lower() == 'true':
            return True
        if text.lower() == 'false':
            return False
        try:
            if '.' in text:
                return float(text)
            return int(text)
        except ValueError:
            return text
    
    def import_config(self):
        """从文件导入配置"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.load_config(config)
            except Exception as e:
                QMessageBox.warning(self, "导入错误", f"无法导入配置: {str(e)}")
    
    def export_config(self):
        """导出配置到文件"""
        config = self.get_config()
        if config:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存配置文件", "", "JSON Files (*.json)")
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                    QMessageBox.information(self, "成功", "配置已保存")
                except Exception as e:
                    QMessageBox.warning(self, "导出错误", f"无法保存配置: {str(e)}")
    
    def load_config(self, config):
        """加载配置到输入框"""
        if 'task_info' in config:
            for key, value in config['task_info'].items():
                if key in self.task_inputs:
                    self.task_inputs[key].setText(str(value))
        
        if 'initial_info' in config:
            for key, value in config['initial_info'].items():
                if key in self.initial_inputs:
                    self.initial_inputs[key].setText(str(value))
        
        if 'old_game' in config:
            for key, value in config['old_game'].items():
                if key in self.old_inputs:
                    self.old_inputs[key].setText(str(value))