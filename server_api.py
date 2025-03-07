import json
from collections import defaultdict

import simu_data_get
from PyQt6.QtCore import QObject, pyqtSignal
from simu_data_get import SimuData
import threading

class TestResultListener(QObject):
    """测试结果监听器"""
    result_updated = pyqtSignal(dict)  # 结果更新信号

    def __init__(self):
        super().__init__()
        self.accumulated_data = defaultdict(lambda: defaultdict(list))

    def on_result_update(self, result):
        """处理结果更新"""
        # 累积数据
        for category, data in result.items():
            self._accumulate_data(category, data)
        
        self.result_updated.emit(self._process_result())

    def on_result_update_others(self, result):
        """处理结果更新"""
        # 直接处理结果
        self.result_updated.emit({
            "status": "completed",
            "results": [{
                "file": "result.txt",
                "status": "completed",
                "content": result,
                "type": "text"
            }]
        })
        # for category, data in result.items():
        #     self._accumulate_data(category, data)
        #
        # self.result_updated.emit(self._process_result())
    
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
        for category, data in self.accumulated_data.items():
            summary_data[category] = {}
            for key, values in data.items():
                if key == 'totalTimes':
                    continue
                summary_data[category][key] = values[-1] if values else 0
        # 如果有汇总数据，添加汇总文件
        if summary_data:
            summary_content = SimuData.print_lab(summary_data)
            processed_result["results"].append({
                "file": "Summary.txt",
                "status": "running",
                "content": summary_content,
                "data_info": summary_data
            })

        # 处理结果
        for category, data in self.accumulated_data.items():
            folder = {
                "name": f"{category} Results",
                "type": "folder",
                "children": []
            }
            times = data['totalTimes']

            for key, values in data.items():
                if key == 'totalTimes':
                    continue
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

                folder["children"].append({
                    "file": f"{key}.txt",
                    "status": "running",
                    "content": "\n".join(table_rows),
                    "series_data": series_data
                })
            processed_result["results"].append(folder)
        
        return processed_result

    def clear_results(self):
        """清空累积的结果数据"""
        self.accumulated_data = defaultdict(lambda: defaultdict(list))

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
        self.method_mapping = {
            'initial_info': (simu_data_get.run, self._handle_initial_result),
            'task_info': (simu_data_get.task_run, self._handle_text_result),
            'old_game': (simu_data_get.old_game_check, self._handle_text_result)
        }
    
    def get_server_list(self) -> list:
        """获取服务器列表（预留接口）"""
        print("调用获取服务器列表接口")
        return self.mock_servers
    
    def update_config(self, server_id: int, files: list, test_config: dict,
                      project_path: str) -> bool:
        """更新服务器配置并启动测试"""
        # 清空之前的结果
        self.result_listener.clear_results()
        
        url = self.get_server_config(server_id)["address"]
        config_type = next(iter(test_config.keys()))  # 获取配置类型
        config_data = test_config[config_type]
        
        # 获取对应的方法和处理器
        method, handler = self.method_mapping.get(config_type, (None, None))
        if not method:
            print(f"未知的配置类型: {config_type}")
            return False
        
        # 在新线程中运行测试
        def run_test():
            method(
                url, 
                config_data,
                callback=self.result_listener.on_result_update
                    if config_type == 'initial_info'
                    else self.result_listener.on_result_update_others,
                project_path=project_path
            )
        
        # 保存线程引用
        self.test_thread = threading.Thread(target=run_test)
        self.test_thread.daemon = True
        self.test_thread.start()
        return True

    def _handle_initial_result(self, result):
        """处理 initial_info 的结果"""
        # 使用现有的处理逻辑
        pass

    def _handle_text_result(self, result):
        """处理文本类型的结果"""
        # 直接返回文本结果
        return str(result)

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
            self.test_thread.join()  # 等待线程结束
            self.test_thread = None
            simu_data_get.set_thread_stop_flag(0)
        
        return True

    def get_server_name(self, server_id):
        for server in self.mock_servers:
            if server["id"] == server_id:
                return f"{server['name']}:{server['address']}"
        return None
