#!/bin/bash

# Git AI Commit v0.2.1 快速发布脚本

echo "🚀 Git AI Commit v0.2.1 快速发布"
echo "================================"

# 检查是否在正确目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查构建文件是否存在
if [ ! -f "dist/git_ai_commit_gui-0.2.1-py3-none-any.whl" ]; then
    echo "❌ 错误：构建文件不存在，请先运行 ./publish.sh"
    exit 1
fi

echo "📋 当前状态："
echo "✅ 项目目录正确"
echo "✅ 构建文件存在"

# 检查环境变量
if [ -n "$UV_PUBLISH_TOKEN" ]; then
    echo "✅ 检测到PyPI token环境变量"
    echo ""
    echo "🚀 开始发布到PyPI..."
    uv publish
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 发布成功！"
        echo ""
        echo "📋 后续步骤："
        echo "1. 等待2-5分钟让PyPI更新"
        echo "2. 测试安装：pip install --upgrade git-ai-commit-gui==0.2.1"
        echo "3. 创建GitHub Release"
        echo "4. 通知用户升级"
    else
        echo "❌ 发布失败，请检查token和网络连接"
        exit 1
    fi
else
    echo "⚠️ 未检测到PyPI token环境变量"
    echo ""
    echo "请先设置token："
    echo "export UV_PUBLISH_TOKEN='your-pypi-token'"
    echo ""
    echo "或者直接发布："
    echo "uv publish --token your-pypi-token"
    echo ""
    echo "获取token：https://pypi.org/manage/account/token/"
fi
