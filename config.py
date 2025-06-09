#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
用于管理应用程序的配置信息，包括API设置、界面设置等
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件名
        """
        self.config_file = Path.home() / ".git_ai_commit" / config_file
        self.config_file.parent.mkdir(exist_ok=True)
        self._config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        default_prompt = """你是一名专业的软件工程师。
仔细审查提供的上下文和即将提交到 Git 仓库的代码变更。
为这些变更生成提交信息。
提交信息必须使用祈使语气（例如"修复"而不是"修复了"）。
提交信息的格式应如下：
使用以下前缀：
- **修复**（fix）
- **功能**（feat）
- **构建**（build）
- **杂项**（chore）
- **持续集成**（ci）
- **文档**（docs）
- **代码样式**（style）
- **重构**（refactor）
- **性能**（perf）
- **测试**（test）
只需回复提交信息本身，不要包含引号、注释或额外说明！
示例：
`修复 用户登录时的空指针异常`
`功能 添加用户注册接口`
`重构 优化订单处理逻辑`"""

        return {
            "api": {
                "url": "https://api.kenhong.com/v1",
                "api_key": "",
                "model": "glm-4-flash",
                "prompt": default_prompt
            },
            "ui": {
                "window_width": 400,
                "window_height": 550,
                "last_repo_path": ""
            },
            "git": {
                "max_diff_lines": 200,
                "auto_stage": False
            }
        }
    
    def load_config(self) -> None:
        """从文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置，保留默认值
                    self._merge_config(self._config, loaded_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"配置文件加载失败，使用默认配置: {e}")
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"配置文件保存失败: {e}")
    
    def _merge_config(self, default: Dict, loaded: Dict) -> None:
        """递归合并配置"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def get(self, key_path: str, default=None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，如 'api.url'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key_path: 配置键路径，如 'api.url'
            value: 配置值
        """
        keys = key_path.split('.')
        config = self._config
        
        # 导航到最后一级
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
    
    def get_api_config(self) -> Dict[str, str]:
        """获取API配置"""
        return {
            "url": self.get("api.url", ""),
            "api_key": self.get("api.api_key", ""),
            "model": self.get("api.model", "glm-4-flash"),
            "prompt": self.get("api.prompt", "")
        }
    
    def set_api_config(self, url: str, api_key: str, model: str, prompt: str = None) -> None:
        """设置API配置"""
        self.set("api.url", url)
        self.set("api.api_key", api_key)
        self.set("api.model", model)
        if prompt is not None:
            self.set("api.prompt", prompt)
        self.save_config()
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return {
            "window_width": self.get("ui.window_width", 800),
            "window_height": self.get("ui.window_height", 600),
            "last_repo_path": self.get("ui.last_repo_path", "")
        }
    
    def set_ui_config(self, **kwargs) -> None:
        """设置UI配置"""
        for key, value in kwargs.items():
            self.set(f"ui.{key}", value)
        self.save_config()
    
    def get_git_config(self) -> Dict[str, Any]:
        """获取Git配置"""
        return {
            "max_diff_lines": self.get("git.max_diff_lines", 200),
            "auto_stage": self.get("git.auto_stage", False)
        }


# 全局配置管理器实例
config_manager = ConfigManager()


if __name__ == "__main__":
    # 测试配置管理器
    print("测试配置管理器...")
    
    # 测试默认配置
    print(f"默认API URL: {config_manager.get('api.url')}")
    print(f"默认窗口大小: {config_manager.get('ui.window_width')}x{config_manager.get('ui.window_height')}")
    
    # 测试设置和获取
    config_manager.set("api.api_key", "test-key")
    print(f"设置后的API Key: {config_manager.get('api.api_key')}")
    
    # 测试API配置
    api_config = config_manager.get_api_config()
    print(f"API配置: {api_config}")
    
    print("配置管理器测试完成")
