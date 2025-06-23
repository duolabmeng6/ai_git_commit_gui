# GitHub Release v0.2.1 发布说明

## 🎉 Git AI Commit v0.2.1 发布

### 📋 版本信息
- **版本号**: v0.2.1
- **发布日期**: 2025-06-23
- **兼容性**: Python 3.12+

### ✨ 主要更新

#### 🐛 重要修复
- **修复Windows编码问题**: 解决了Windows环境下`UnicodeDecodeError: 'gbk' codec can't decode byte 0xa7`错误
- **增强跨平台兼容性**: 添加了智能编码检测和多编码支持
- **改进错误处理**: 提供更好的编码错误处理和调试信息

#### 🔧 技术改进
- 新增 `safe_subprocess_run()` 函数，支持UTF-8、GBK、GB2312等多种编码
- 优化了所有Git命令调用的编码处理
- 增强了Windows中文环境下的稳定性

#### 🚀 自动模式优化
- 修复了`--auto`模式在Windows环境下的编码问题
- 提升了自动提交流程的可靠性
- 改进了错误信息的显示

### 🚀 升级方法

#### 使用 uv tool (推荐)
```bash
uv tool upgrade git-ai-commit-gui
```

#### 使用 pip
```bash
pip install --upgrade git-ai-commit-gui
```

#### 从源码升级
```bash
git pull origin main
uv sync
```

### 📦 下载

- **Wheel包**: `git_ai_commit_gui-0.2.1-py3-none-any.whl`
- **源码包**: `git_ai_commit_gui-0.2.1.tar.gz`

### 🔗 相关链接

- [PyPI页面](https://pypi.org/project/git-ai-commit-gui/)
- [升级指南](UPGRADE_GUIDE.md)
- [构建指南](BUILD_GUIDE.md)
- [使用文档](README.md)

### 🐛 问题反馈

如果在升级或使用过程中遇到问题，请：
1. 查看 [升级指南](UPGRADE_GUIDE.md)
2. 提交 [GitHub Issue](https://github.com/duolabmeng6/ai_git_commit_gui/issues)
3. 联系开发者: 1715109585@qq.com

### 🙏 致谢

感谢所有用户的支持和反馈！

---

**完整更新日志**: https://github.com/duolabmeng6/ai_git_commit_gui/compare/v0.2.0...v0.2.1
