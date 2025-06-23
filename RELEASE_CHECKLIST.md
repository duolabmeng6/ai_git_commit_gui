# Git AI Commit v0.2.1 发布检查清单

## ✅ 预发布检查
- [x] 版本号已更新到 0.2.1
- [x] 编码修复代码已实现并测试
- [x] 包构建成功
- [x] 命令行工具测试通过
- [x] 发布说明已更新

## 🚀 发布步骤

### 1. 发布到PyPI
```bash
# 方法1：使用环境变量（推荐）
export UV_PUBLISH_TOKEN='your-pypi-token'
uv publish

# 方法2：直接指定token
uv publish --token YOUR_PYPI_TOKEN

# 方法3：先测试发布
uv publish --index testpypi --token YOUR_TEST_PYPI_TOKEN
```

### 2. 验证发布
```bash
# 等待几分钟后测试安装
pip install --upgrade git-ai-commit-gui==0.2.1

# 或使用uv
uv tool install git-ai-commit-gui==0.2.1 --force
```

### 3. 创建GitHub Release
- 使用 `create_release.md` 中的内容
- 上传构建的wheel和tar.gz文件
- 标签：v0.2.1

### 4. 测试新版本
```bash
# 测试基本功能
git-ai-commit-gui --help

# 测试自动模式（Windows用户重点测试）
git-ai-commit-gui --auto
```

## 🐛 本次修复内容
- 修复Windows环境下的UnicodeDecodeError编码问题
- 添加智能编码检测和多编码支持
- 增强--auto模式稳定性
- 改进错误处理和调试信息

## 📋 发布后任务
- [ ] 发布到PyPI
- [ ] 创建GitHub Release
- [ ] 通知用户升级
- [ ] 更新文档
- [ ] 监控用户反馈

## 🔗 相关链接
- PyPI页面: https://pypi.org/project/git-ai-commit-gui/
- GitHub仓库: https://github.com/duolabmeng6/ai_git_commit_gui
- 问题反馈: https://github.com/duolabmeng6/ai_git_commit_gui/issues
