#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI接口模块
提供与GLM-4-Flash AI模型的交互功能
"""

import json
import requests
from typing import Optional, Dict, Any
import time
import os


class GLMInterface:
    """GLM-4-Flash AI接口类"""
    
    def __init__(self, api_key, base_url: str = "https://api.kenhong.com/v1", model: str = "glm-4-flash"):
        """
        初始化AI接口

        Args:
            api_key: API密钥
            base_url: API基础URL
            model: AI模型名称
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = 30
        self.max_retries = 3
    
    def call_ai(self, prompt: str, content: str, 
                temperature: float = 0.7, 
                max_tokens: int = 2000) -> Optional[str]:
        """
        调用AI接口进行文本处理
        
        Args:
            prompt: 提示词
            content: 要处理的内容
            temperature: 温度参数，控制输出随机性
            max_tokens: 最大输出token数
            
        Returns:
            AI的响应文本，失败时返回None
        """
        try:
            # 构建请求消息
            messages = [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user", 
                    "content": content
                }
            ]
            
            # 构建请求数据
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求（带重试机制）
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=request_data,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 检查响应格式
                        if "choices" in result and len(result["choices"]) > 0:
                            return result["choices"][0]["message"]["content"].strip()
                        else:
                            print(f"警告: 响应格式异常: {result}")
                            return None
                    
                    elif response.status_code == 429:  # 速率限制
                        wait_time = 2 ** attempt  # 指数退避
                        print(f"速率限制，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    
                    else:
                        print(f"API请求失败: {response.status_code}")
                        print(f"响应内容: {response.text}")
                        return None
                
                except requests.exceptions.Timeout:
                    print(f"请求超时，尝试 {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        print("请求超时，已达到最大重试次数")
                        return None
                
                except requests.exceptions.RequestException as e:
                    print(f"网络请求错误: {e}")
                    return None
            
            return None
            
        except Exception as e:
            print(f"AI接口调用失败: {e}")
            return None
    
   
    def generate_commit_message(self, git_analysis: str, custom_prompt: str = None) -> Optional[str]:
        """
        生成Git提交消息

        Args:
            git_analysis: Git分析结果
            custom_prompt: 自定义提示词，如果为None则使用默认提示词

        Returns:
            建议的提交消息
        """
        if custom_prompt:
            prompt = custom_prompt
        else:
            # 默认提示词
            prompt = """你是一名专业的软件工程师。
仔细审查提供的上下文和即将提交到 Git 仓库的代码变更。
为这些变更生成提交信息。
提交信息必须使用祈使语气（例如“修复”而不是“修复了”）。
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

        return self.call_ai(prompt, git_analysis, temperature=0.3)
    

def create_ai_interface(api_key, base_url: str = "https://api.kenhong.com/v1", model: str = "glm-4-flash") -> GLMInterface:
    """
    创建AI接口实例

    Args:
        api_key: API密钥
        base_url: API基础URL
        model: AI模型名称

    Returns:
        GLMInterface实例
    """
    return GLMInterface(api_key, base_url, model)


def test_ai_interface():
    """测试AI接口功能"""
    # 这里需要实际的API密钥
    api_key = "your-api-key-here"
    
    if api_key == "your-api-key-here":
        print("请设置有效的API密钥进行测试")
        return
    
    ai = create_ai_interface(api_key)
    
    # 测试基本调用
    test_content = """
    文件: main.py (修改)
    变更内容:
    + def new_function():
    +     return "Hello World"
    - def old_function():
    -     return "Goodbye"
    """
    
    print("测试AI总结功能...")
    summary = ai.summarize_git_changes(test_content)
    if summary:
        print("AI总结结果:")
        print(summary)
    else:
        print("AI总结失败")
    
    print("\n测试提交消息生成...")
    commit_msg = ai.generate_commit_message(test_content)
    if commit_msg:
        print("建议的提交消息:")
        print(commit_msg)
    else:
        print("提交消息生成失败")


def demo_commit_message():
    """演示提交消息生成功能"""
    print("\n\n📝 提交消息生成演示")
    print("=" * 50)
    sample_changes = """
文件: src/auth.py (修改)
- 修复了用户登录验证的bug
- 添加了密码强度检查
- 优化了错误处理逻辑
文件: tests/test_auth.py (新增)
- 添加了用户认证的单元测试
- 覆盖了各种边界情况
"""
    api_key = os.getenv("GLM_API_KEY", "")
    if not api_key:
        print("⚠️  需要API密钥，跳过演示")
        return
    try:
        print("🔄 正在生成提交消息...")
        ai = GLMInterface(api_key)
        commit_msg = ai.generate_commit_message(sample_changes)
        if commit_msg:
            print("\n✅ 建议的提交消息:")
            print("-" * 30)
            print(commit_msg)
            print("-" * 30)
        else:
            print("\n❌ 提交消息生成失败")
    except Exception as e:
        print(f"\n❌ 提交消息生成失败: {e}")



if __name__ == "__main__":
    demo_commit_message()
