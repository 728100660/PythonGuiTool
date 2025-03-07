# 服务器配表更新GUI系统

这是一个基于Python和PyQt6开发的服务器配置表更新工具，支持文件对比、自动化测试和结果展示。

## 系统架构

系统采用MVC（Model-View-Controller）架构设计，主要分为以下几个核心模块：

### 1. 数据层 (Model)

#### 1.1 数据库模块 (database.py)
- 使用SQLite3实现文件版本管理
- 主要表结构：
  - file_versions: 存储文件历史版本
  - servers: 存储服务器信息
- 核心功能：
  - 文件版本存储和检索
  - 文件历史记录管理

#### 1.2 文件管理模块 (file_manager.py)
- 负责文件系统操作
- 实现文件树结构生成
- 文件变更检测
- 版本对比功能

#### 1.3 服务器API模块 (server_api.py)
- 预留服务器接口实现
- 当前使用模拟数据
- 主要接口：
  - 获取服务器列表
  - 更新配置文件
  - 获取测试结果

### 2. 视图层 (View)

#### 2.1 主窗口 (main_window.py)
- 三栏式布局设计：
  - 左侧：服务器列表
  - 中间：文件树
  - 右侧：文件对比和测试结果
- 主要组件：
  - 服务器树形视图
  - 文件树形视图
  - 文件对比视图
  - 测试结果展示区

### 3. 控制层 (Controller)

#### 3.1 主程序入口 (main.py)
- 初始化应用程序
- 组装各个模块
- 启动主窗口

## 数据流设计

1. 文件版本管理流程：
   ```
   选择工程目录 -> 扫描文件 -> 对比数据库版本 -> 显示变更
   ```

2. 配置更新流程：
   ```
   选择服务器 -> 选择文件 -> 提交更新 -> 等待测试结果 -> 显示结果
   ```

## 关键功能实现

### 1. 文件版本管理
- 使用MD5哈希存储文件特征
- 使用BLOB类型存储文件内容
- 支持历史版本查询

### 2. 文件树显示
- 递归遍历目录结构
- 过滤隐藏文件
- 动态更新变更状态

### 3. 服务器管理
- 支持多服务器配置
- 状态实时显示
- 批量更新功能

## 预留接口说明

### 1. 服务器API

## 安装和使用

### 环境要求
- Python 3.10
- PyQt6

### 安装依赖
```bash
pip install PyQt6
```
还有安装node.js  v18.15.0

### 运行程序
```bash
python main.py
```

## 使用流程

1. 启动程序
2. 选择工程目录
3. 从左侧服务器列表选择目标服务器
4. 在文件树中查看和选择需要更新的文件
5. 点击提交按钮进行更新
6. 查看测试结果

## 注意事项

1. 首次运行会自动创建SQLite数据库
2. 预留接口当前使用模拟数据
3. 文件对比功能支持二进制文件
4. 支持批量更新多个服务器

## 使用注意事项
1. 不能同时开启两个更新页签，每次只进行一次提交结果页签展示，如果需要测试下一个机台，则需要关闭当前正在测试的结果页签