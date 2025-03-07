import json
import simu_data_get
from PyQt6.QtCore import QObject, pyqtSignal
from simu_data_get import SimuData
import threading

class TestResultListener(QObject):
    """测试结果监听器"""
    result_updated = pyqtSignal(dict)  # 结果更新信号

    def __init__(self):
        super().__init__()
        self.accumulated_data = {
            'overall': {'totalTimes': []},
            'FG': {'totalTimes': []}
        }

    def on_result_update(self, result):
        """处理结果更新"""
        # 累积数据
        if 'overall' in result:
            self._accumulate_data('overall', result['overall'])
        if 'FG' in result:
            self._accumulate_data('FG', result['FG'])
        
        self.result_updated.emit(self._process_result())
    
    def _accumulate_data(self, category, data):
        """累积数据"""
        times = data.get('totalTimes', 0)
        if times not in self.accumulated_data[category]['totalTimes']:
            self.accumulated_data[category]['totalTimes'].append(times)
            for key, value in data.items():
                if key != 'totalTimes':
                    if key not in self.accumulated_data[category]:
                        self.accumulated_data[category][key] = []
                    self.accumulated_data[category][key].append(value)

    def _process_result(self):
        """处理累积的结果"""
        processed_result = {
            "status": "running",
            "results": []
        }
        
        # 创建汇总数据
        summary_data = {}
        if self.accumulated_data['overall']['totalTimes']:
            summary_data['Overall'] = {}
            for key, values in self.accumulated_data['overall'].items():
                if key != 'totalTimes':
                    summary_data['Overall'][key] = values[-1] if values else 0
        
        if self.accumulated_data['FG']['totalTimes']:
            summary_data['FG'] = {}
            for key, values in self.accumulated_data['FG'].items():
                if key != 'totalTimes':
                    summary_data['FG'][key] = values[-1] if values else 0
        
        # 如果有汇总数据，添加汇总文件
        if summary_data:
            summary_content = SimuData.print_lab(summary_data)
            processed_result["results"].append({
                "file": "Summary.txt",
                "status": "running",
                "content": summary_content,
                "data_info": summary_data
            })

        # 处理 overall 结果
        if self.accumulated_data['overall']['totalTimes']:
            overall_folder = {
                "name": "Overall Results",
                "type": "folder",
                "children": []
            }
            
            overall = self.accumulated_data['overall']
            times = overall['totalTimes']
            
            for key, values in overall.items():
                if key != 'totalTimes':
                    series_data = {
                        "name": key,
                        "data": list(zip(times, values))
                    }
                    
                    # 生成表格内容
                    table_rows = []
                    table_rows.append(f"{'次数':<10}\t{key:<15}")
                    table_rows.append("-" * 30)
                    for t, v in zip(times, values):
                        table_rows.append(f"{int(t):<10}\t{float(v):<15.2f}")
                    
                    overall_folder["children"].append({
                        "file": f"{key}.txt",
                        "status": "running",
                        "content": "\n".join(table_rows),
                        "series_data": series_data
                    })
            
            processed_result["results"].append(overall_folder)
        
        # 处理 FG 结果
        if self.accumulated_data['FG']['totalTimes']:
            fg_folder = {
                "name": "FG Results",
                "type": "folder",
                "children": []
            }
            
            fg = self.accumulated_data['FG']
            times = self.accumulated_data['FG']['totalTimes']
            
            for key, values in fg.items():
                if key != 'totalTimes':
                    series_data = {
                        "name": key,
                        "data": list(zip(times, values))
                    }
                    
                    # 生成表格内容
                    table_rows = []
                    table_rows.append(f"{'次数':<10}\t{key:<15}")
                    table_rows.append("-" * 30)
                    for t, v in zip(times, values):
                        table_rows.append(f"{int(t):<10}\t{float(v):<15.2f}")
                    
                    fg_folder["children"].append({
                        "file": f"{key}.txt",
                        "status": "running",
                        "content": "\n".join(table_rows),
                        "series_data": series_data
                    })
            
            processed_result["results"].append(fg_folder)
        
        return processed_result

class ServerAPI:
    def __init__(self):
        # 模拟服务器列表数据
        self.mock_servers = [
            {"id": 1, "name": "测试服务器1", "address": "http://192.168.30.74:8094/"},
            {"id": 2, "name": "测试服务器2", "address": "http://192.168.30.13:8095/"},
            {"id": 3, "name": "测试服务器3", "address": "http://192.168.30.68:8096/"},
            {"id": 4, "name": "开发环境", "address": "http://192.168.30.121:8093/"}
        ]
        self.result_listener = TestResultListener()
        self.test_thread = None  # 添加线程引用
    
    def get_server_list(self) -> list:
        """获取服务器列表（预留接口）"""
        print("调用获取服务器列表接口")
        return self.mock_servers
    
    def update_config(self, server_id: int, files: list, test_config: dict,
                      project_path: str) -> bool:
        """更新服务器配置并启动测试"""
        url = self.get_server_config(server_id)["address"]
        task_info = test_config.get("task_info", {})
        initial_info = test_config.get("initial_info", {})
        old_game = test_config.get("old_game", {})
        
        # 在新线程中运行测试
        def run_test():
            simu_data_get.run(
                url, task_info, initial_info, old_game,
                callback=self.result_listener.on_result_update,
                project_path=project_path
            )
        
        # 保存线程引用
        self.test_thread = threading.Thread(target=run_test)
        self.test_thread.daemon = True
        self.test_thread.start()
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

    def stop_test(self, server_id: int, game_id: int) -> bool:
        """停止测试"""
        url = self.get_server_config(server_id)["address"]
        print(f"停止服务器 {server_id} 的测试")
        
        # 停止测试线程
        if self.test_thread and self.test_thread.is_alive():
            simu_data_get.stop_bet(url, game_id)  # 调用停止接口
            simu_data_get.set_thread_stop_flag(1)
            self.test_thread.join(timeout=1)  # 等待线程结束
            self.test_thread = None
            simu_data_get.set_thread_stop_flag(0)
        
        return True

    def get_server_name(self, server_id):
        for server in self.mock_servers:
            if server["id"] == server_id:
                return f"{server['name']}:{server['address']}"
        return None
