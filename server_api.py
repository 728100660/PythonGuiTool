import json
import simu_data_get
from PyQt6.QtCore import QObject, pyqtSignal
import threading

class TestResultListener(QObject):
    """测试结果监听器"""
    result_updated = pyqtSignal(dict)  # 结果更新信号

    def on_result_update(self, result):
        """处理结果更新"""
        self.result_updated.emit(self._process_result(result))
    
    def _process_result(self, result):
        """处理单次结果"""
        processed_result = {
            "status": "running",
            "results": []
        }
        
        if "overall" in result:
            overall = result["overall"]
            data_points = []
            for key, value in overall.items():
                if key != "totalTimes":
                    data_points.append({
                        "name": key,
                        "data": [(overall["totalTimes"], value)]
                    })
            
            # 生成结果文本和数据系列
            for series in data_points:
                content_lines = []
                for x, y in series["data"]:
                    content_lines.append(f"{x}次，{series['name']}为{y}")
                
                processed_result["results"].append({
                    "file": f"overall_{series['name']}.txt",
                    "status": "running",
                    "content": "\n".join(content_lines),
                    "series_data": series
                })
        
        return processed_result

class ServerAPI:
    def __init__(self):
        # 模拟服务器列表数据
        self.mock_servers = [
            {"id": 1, "name": "测试服务器1", "address": "http://192.168.30.68:8094/"},
            {"id": 2, "name": "测试服务器2", "address": "http://192.168.30.68:8095/"},
            {"id": 3, "name": "测试服务器3", "address": "http://192.168.30.68:8096/"}
        ]
        self.result_listener = TestResultListener()
    
    def get_server_list(self) -> list:
        """获取服务器列表（预留接口）"""
        print("调用获取服务器列表接口")
        return self.mock_servers
    
    def update_config(self, server_id: int, files: list, test_config: dict) -> bool:
        """更新服务器配置并启动测试"""
        url = self.get_server_config(server_id)["address"]
        task_info = test_config["task_info"]
        initial_info = test_config["initial_info"]
        old_game = test_config["old_game"]
        
        # 在新线程中运行测试
        def run_test():
            simu_data_get.run(
                url, task_info, initial_info, old_game,
                callback=self.result_listener.on_result_update
            )
        
        thread = threading.Thread(target=run_test)
        thread.daemon = True
        thread.start()
        return True

    def _process_test_results(self, results: dict) -> dict:
        """处理测试结果数据"""
        processed_results = {
            "status": "success",
            "results": []
        }
        
        # 处理总体结果
        if "overall" in results:
            overall = results["overall"]
            content_lines = []
            
            # 提取所有数据点
            data_points = []
            for key, value in overall.items():
                if key != "totalTimes":  # 跳过totalTimes，它将作为X轴
                    data_points.append({
                        "name": key,
                        "data": list(zip(overall["totalTimes"], value))
                    })
            
            # 生成结果文本
            for point in data_points[0]["data"]:  # 使用第一个数据系列的点数
                total_times = point[0]
                line_parts = [f"{total_times}次"]
                for series in data_points:
                    value = next(p[1] for p in series["data"] if p[0] == total_times)
                    line_parts.append(f"{series['name']}为{value}")
                content_lines.append("，".join(line_parts))
            
            # 添加到结果列表
            for i, series in enumerate(data_points):
                processed_results["results"].append({
                    "file": f"overall_{series['name']}.txt",
                    "status": "passed",
                    "content": "\n".join(content_lines),
                    "series_data": series
                })
        
        return processed_results

    def get_server_config(self, server_id: int) -> dict:
        """通过id获取服务器配置"""
        for server in self.mock_servers:
            if server["id"] == server_id:
                return server
        return None

    def get_test_results(self, server_id: int) -> dict:
        """获取测试结果"""
        return self.test_results if hasattr(self, 'test_results') else {
            "status": "error",
            "results": []
        } 