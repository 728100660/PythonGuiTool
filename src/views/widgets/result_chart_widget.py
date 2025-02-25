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
        
        # 存储初始范围
        self.initial_x_range = (0, 0)
        self.initial_y_range = (0, 0)
        
        # 创建图表
        self.chart = QChart()
        self.chart.setTitle("测试结果统计")
        self.chart.setTitleFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setMargins(QMargins(10, 10, 10, 10))
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # 创建数据系列
        series = QSplineSeries()  # 使用样条曲线，更平滑
        series.setName("中奖次数")
        pen = QPen(QColor("#1f77b4"))  # 设置更专业的颜色
        pen.setWidth(3)
        series.setPen(pen)
        
        # 解析结果文本
        data_points = self.parse_results(results_text)
        
        # 添加数据点
        max_x = 0
        max_y = 0
        points = []
        for total, wins in data_points:
            points.append(QPointF(total, wins))
            max_x = max(max_x, total)
            max_y = max(max_y, wins)
        series.replace(points)  # 批量添加点，性能更好
        
        # 保存初始范围
        self.initial_x_range = (0, max_x * 1.1)
        self.initial_y_range = (0, max_y * 1.1)
        
        # 添加系列到图表
        self.chart.addSeries(series)
        
        # 创建X轴
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("测试次数")
        self.axis_x.setTitleFont(QFont("Microsoft YaHei", 10))
        self.axis_x.setRange(*self.initial_x_range)
        self.axis_x.setTickCount(10)
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setLabelsFont(QFont("Microsoft YaHei", 9))
        self.axis_x.setGridLineVisible(True)
        self.axis_x.setMinorGridLineVisible(True)
        
        # 创建Y轴
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("中奖次数")
        self.axis_y.setTitleFont(QFont("Microsoft YaHei", 10))
        self.axis_y.setRange(*self.initial_y_range)
        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%d")
        self.axis_y.setLabelsFont(QFont("Microsoft YaHei", 9))
        self.axis_y.setGridLineVisible(True)
        self.axis_y.setMinorGridLineVisible(True)
        
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)
        
        # 创建图表视图
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        
        # 添加到布局
        layout.addWidget(self.chart_view)
        
        # 添加原始数据显示
        text_view = QTextEdit()
        text_view.setReadOnly(True)
        text_view.setText(results_text)
        text_view.setMaximumHeight(100)
        text_view.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(text_view)
        
        # 连接鼠标滚轮事件
        self.chart_view.wheelEvent = self.handle_wheel_event
        
        # 存储当前视图矩形
        self.current_rect = QRectF(*self.initial_x_range, *self.initial_y_range)
    
    def handle_wheel_event(self, event):
        """处理鼠标滚轮事件，保持原点位置固定"""
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        
        # 获取鼠标位置
        pos = event.position()
        scene_pos = self.chart_view.mapToScene(pos.toPoint())
        chart_pos = self.chart.mapFromScene(scene_pos)
        
        # 计算新的范围
        current_x_min = self.axis_x.min()
        current_x_max = self.axis_x.max()
        current_y_min = self.axis_y.min()
        current_y_max = self.axis_y.max()
        
        # 确保原点固定
        new_x_min = 0  # 固定X轴最小值为0
        new_x_max = current_x_max * factor
        new_y_min = 0  # 固定Y轴最小值为0
        new_y_max = current_y_max * factor
        
        # 设置新的范围
        self.axis_x.setRange(new_x_min, new_x_max)
        self.axis_y.setRange(new_y_min, new_y_max)
        
        # 更新当前视图矩形
        self.current_rect = QRectF(new_x_min, new_y_min, 
                                 new_x_max - new_x_min, 
                                 new_y_max - new_y_min)
    
    def reset_zoom(self):
        """重置缩放"""
        self.axis_x.setRange(*self.initial_x_range)
        self.axis_y.setRange(*self.initial_y_range)
        self.current_rect = QRectF(*self.initial_x_range, *self.initial_y_range)
    
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