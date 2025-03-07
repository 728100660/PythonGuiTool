from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QGroupBox, QFormLayout, QFileDialog)
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


        task_tab = QWidget()
        task_layout = QFormLayout(task_tab)
        for label, input_field in self.config_inputs.items():
            task_layout.addRow(label, input_field)
        tab_widget.addTab(task_tab, self.config_type)
        #
        # # Task Info 选项卡
        # task_tab = QWidget()
        # task_layout = QFormLayout(task_tab)
        # self.task_inputs = self.create_input_group(self.task_info)
        # for label, input_field in self.task_inputs.items():
        #     task_layout.addRow(label, input_field)
        # tab_widget.addTab(task_tab, "Task Info")
        #
        # # Initial Info 选项卡
        # initial_tab = QWidget()
        # initial_layout = QFormLayout(initial_tab)
        # self.initial_inputs = self.create_input_group(self.initial_info)
        # for label, input_field in self.initial_inputs.items():
        #     initial_layout.addRow(label, input_field)
        # tab_widget.addTab(initial_tab, "Initial Info")
        #
        # # Old Game 选项卡
        # old_tab = QWidget()
        # old_layout = QFormLayout(old_tab)
        # self.old_inputs = self.create_input_group(self.old_game)
        # for label, input_field in self.old_inputs.items():
        #     old_layout.addRow(label, input_field)
        # tab_widget.addTab(old_tab, "Old Game")
        
        layout.addWidget(tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 添加导入/导出按钮
        import_btn = QPushButton("导入配置")
        export_btn = QPushButton("导出配置")
        import_btn.clicked.connect(self.import_config)
        export_btn.clicked.connect(self.export_config)
        button_layout.addWidget(import_btn)
        button_layout.addWidget(export_btn)
        
        # 添加确定/取消按钮
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_input_group(self, data):
        """创建输入字段组"""
        inputs = {}
        for key, value in data.items():
            input_field = QLineEdit()
            if isinstance(value, bool):
                input_field.setText(str(value).lower())
            else:
                input_field.setText(str(value))
            inputs[key] = input_field
        return inputs
    
    def get_config(self):
        """获取配置数据"""
        try:
            # task_info = {k: self.parse_value(v.text())
            #             for k, v in self.task_inputs.items()}
            # initial_info = {k: self.parse_value(v.text())
            #               for k, v in self.initial_inputs.items()}
            # old_game = {k: self.parse_value(v.text())
            #            for k, v in self.old_inputs.items()}
            config_type_input = {k: self.parse_value(v.text())
                       for k, v in self.config_inputs.items()}

            return {
                # 'task_info': task_info,
                # 'initial_info': initial_info,
                # 'old_game': old_game,
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