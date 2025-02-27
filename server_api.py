import json

class ServerAPI:
    def __init__(self):
        # 模拟服务器列表数据
        self.mock_servers = [
            {"id": 1, "name": "测试服务器1", "address": "test1.example.com"},
            {"id": 2, "name": "测试服务器2", "address": "test2.example.com"},
            {"id": 3, "name": "正式服务器1", "address": "prod1.example.com"}
        ]
    
    def get_server_list(self) -> list:
        """获取服务器列表（预留接口）"""
        print("调用获取服务器列表接口")
        return self.mock_servers
    
    def update_config(self, server_id: int, files: list, test_config: dict) -> bool:
        """更新服务器配置（预留接口）"""
        print(f"调用更新配置接口 - 服务器ID: {server_id}, 文件列表: {files}")
        print(f"测试配置: {json.dumps(test_config, indent=2, ensure_ascii=False)}")
        return True
    
    def get_test_results(self, server_id: int) -> dict:
        """获取测试结果（预留接口）"""
        print(f"调用获取测试结果接口 - 服务器ID: {server_id}")
        # 模拟测试结果
        return {
            "status": "success",
            "results": [
                {
                    "file": "test1.txt",
                    "status": "passed",
                    "content": "100次，中奖数为30次\n200次，中奖数为65次\n300次，中奖数为95次\n400次，中奖数为125次"
                },
                {
                    "file": "test2.txt",
                    "status": "passed",
                    "content": "100次，中奖数为28次\n200次，中奖数为58次\n300次，中奖数为89次\n400次，中奖数为120次"
                }
            ]
        } 