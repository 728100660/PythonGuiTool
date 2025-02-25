from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCharts import (QChart, QChartView, QLineSeries, QValueAxis, 
                           QSplineSeries)
from PyQt6.QtCore import Qt, QPointF, QMargins, QRectF
from PyQt6.QtGui import QPainter, QPen, QFont, QColor
import re

class ResultChartWidget(QWidget):
    """测试结果图表显示"""
    def __init__(self, results_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        
        # 添加原始数据显示
        text_view = QTextEdit()
        text_view.setReadOnly(True)
        text_view.setText(results_text)
        text_view.setMaximumHeight(100)
        text_view.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(text_view)

    
    def parse_results(self, text):
        """解析结果文本，返回(总次数, 中奖次数)列表"""
        data_points = []
        pattern = r'(\d+)次，中奖数为(\d+)次'
        matches = re.finditer(pattern, text)
        for match in matches:
            total = int(match.group(1))
            wins = int(match.group(2))
            data_points.append((total, wins))
        return sorted(data_points)  # 按总次数排序 