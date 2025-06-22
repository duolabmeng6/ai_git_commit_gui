#!/bin/bash

# Git AI Commit 发布脚本
# 用于自动化发布流程

set -e  # 遇到错误立即退出

echo "🚀 开始发布 Git AI Commit v0.2.0..."

# 检查当前版本
echo "📋 检查当前版本..."
current_version=$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
echo "当前版本: $current_version"

# 清理旧的构建产物
echo "🧹 清理旧的构建产物..."
rm -rf dist/ build/ *.egg-info/

# 构建新版本
echo "🔨 构建新版本..."
uv build

# 验证构建结果
echo "✅ 验证构建结果..."
ls -la dist/

# 测试包安装
echo "🧪 测试包安装..."
uv run --with ./dist/git_ai_commit_gui-${current_version}-py3-none-any.whl --no-project -- python -c "import gui_main; print('✅ 包导入成功')"

# 测试命令行工具
echo "🧪 测试命令行工具..."
uv run --with ./dist/git_ai_commit_gui-${current_version}-py3-none-any.whl --no-project -- git-ai-commit-gui --help > /dev/null && echo "✅ 命令行工具正常"

echo ""
echo "🎯 构建完成！现在可以发布到PyPI："
echo ""
echo "📋 发布选项："
echo "1. 发布到测试环境 (推荐先测试):"
echo "   uv publish --index testpypi --token YOUR_TEST_PYPI_TOKEN"
echo ""
echo "2. 发布到正式PyPI:"
echo "   uv publish --token YOUR_PYPI_TOKEN"
echo ""
echo "3. 使用环境变量 (推荐):"
echo "   export UV_PUBLISH_TOKEN='your-pypi-token'"
echo "   uv publish"
echo ""

# 检查是否设置了环境变量
if [ -n "$UV_PUBLISH_TOKEN" ]; then
    echo "🔑 检测到PyPI token环境变量"
    read -p "是否立即发布到正式PyPI? (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        echo "🚀 发布到PyPI..."
        uv publish
        echo "✅ 发布成功！"
        
        echo ""
        echo "📋 后续步骤："
        echo "1. 创建GitHub Release"
        echo "2. 通知用户升级"
        echo "3. 更新文档"
    else
        echo "⏸️  取消发布"
    fi
elif [ -n "$UV_PUBLISH_TOKEN_TESTPYPI" ]; then
    echo "🔑 检测到测试PyPI token环境变量"
    read -p "是否发布到测试PyPI? (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        echo "🧪 发布到测试PyPI..."
        uv publish --index testpypi
        echo "✅ 测试发布成功！"
    else
        echo "⏸️  取消测试发布"
    fi
else
    echo "⚠️  未检测到PyPI token环境变量"
    echo "请设置以下环境变量之一："
    echo "  export UV_PUBLISH_TOKEN='your-pypi-token'          # 正式PyPI"
    echo "  export UV_PUBLISH_TOKEN_TESTPYPI='your-test-token' # 测试PyPI"
fi

echo ""
echo "🎉 发布脚本执行完成！"
