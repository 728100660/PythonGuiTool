from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QChartView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
import re

class ResultChartWidget(QWidget):
    """测试结果图表显示"""
    def __init__(self, results_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # 创建图表
        chart = QChart()
        chart.setTitle("测试结果统计")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # 创建数据系列
        series = QLineSeries()
        series.setName("中奖次数")
        
        # 解析结果文本
        data_points = self.parse_results(results_text)
        
        # 添加数据点
        max_x = 0
        max_y = 0
        for total, wins in data_points:
            series.append(total, wins)
            max_x = max(max_x, total)
            max_y = max(max_y, wins)
        
        # 添加系列到图表
        chart.addSeries(series)
        
        # 创建坐标轴
        axis_x = QValueAxis()
        axis_x.setTitleText("测试次数")
        axis_x.setRange(0, max_x * 1.1)
        axis_x.setTickCount(10)
        axis_x.setLabelFormat("%d")  # 显示完整数字
        
        axis_y = QValueAxis()
        axis_y.setTitleText("中奖次数")
        axis_y.setRange(0, max_y * 1.1)
        axis_y.setLabelFormat("%d")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        # 创建图表视图
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 允许缩放
        chart_view.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        
        # 添加到布局
        layout.addWidget(chart_view)
        
        # 添加原始数据显示
        text_view = QTextEdit()
        text_view.setReadOnly(True)
        text_view.setText(results_text)
        text_view.setMaximumHeight(100)
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