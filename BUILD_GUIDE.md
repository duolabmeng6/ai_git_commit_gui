# Git AI Commit 构建和发布指南

本指南介绍如何使用 uv 构建和发布 Git AI Commit 包。

## 前置要求

1. 安装 uv：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 确保项目已准备好打包：
- ✅ `pyproject.toml` 已配置完整
- ✅ `README.md` 存在
- ✅ `LICENSE` 文件存在
- ✅ 所有源代码文件就位

## 构建包

### 1. 清理之前的构建产物
```bash
rm -rf dist/ build/ *.egg-info/
```

### 2. 构建包
```bash
uv build
```

这将在 `dist/` 目录中生成：
- 源代码分发包 (`.tar.gz`)
- 二进制分发包 (`.whl`)

### 3. 验证构建结果
```bash
ls -la dist/
```

应该看到类似以下文件：
```
git_ai_commit_gui-0.1.0-py3-none-any.whl
git_ai_commit_gui-0.1.0.tar.gz
```

## 测试包

### 1. 在隔离环境中测试安装
```bash
uv run --with ./dist/git_ai_commit_gui-0.1.0-py3-none-any.whl --no-project -- python -c "import gui_main; print('导入成功')"
```

### 2. 测试命令行工具
```bash
uv run --with ./dist/git_ai_commit_gui-0.1.0-py3-none-any.whl --no-project -- git-ai-commit-gui --help
```

## 发布到 PyPI

### 1. 准备 PyPI 账户
- 注册 [PyPI](https://pypi.org/) 账户
- 生成 API Token：Account settings → API tokens → Add API token

### 2. 发布到测试环境 (推荐)
```bash
uv publish --index testpypi --token YOUR_TEST_PYPI_TOKEN
```

### 3. 从测试环境安装验证
```bash
uv run --with git-ai-commit-gui --index https://test.pypi.org/simple/ --no-project -- git-ai-commit-gui
```

### 4. 发布到正式 PyPI
```bash
uv publish --token YOUR_PYPI_TOKEN
```

## 环境变量配置

为了方便使用，可以设置环境变量：

```bash
# 设置 PyPI Token
export UV_PUBLISH_TOKEN="your-pypi-token-here"

# 设置测试 PyPI Token
export UV_PUBLISH_TOKEN_TESTPYPI="your-test-pypi-token-here"
```

然后可以简化发布命令：
```bash
# 发布到测试环境
uv publish --index testpypi

# 发布到正式环境
uv publish
```

## 版本管理

### 更新版本号
编辑 `pyproject.toml` 中的版本号：
```toml
[project]
version = "0.1.1"  # 更新版本号
```

### 版本号规范
遵循 [语义化版本](https://semver.org/lang/zh-CN/)：
- `0.1.0` → `0.1.1` (补丁版本)
- `0.1.0` → `0.2.0` (次版本)
- `0.1.0` → `1.0.0` (主版本)

## 常见问题

### Q: 构建失败怎么办？
A: 检查：
- `pyproject.toml` 语法是否正确
- 所有依赖是否已安装
- 源代码是否有语法错误

### Q: 发布失败怎么办？
A: 检查：
- API Token 是否正确
- 版本号是否已存在
- 网络连接是否正常

### Q: 如何撤回已发布的版本？
A: PyPI 不允许删除已发布的版本，只能发布新版本。

## 自动化发布

可以使用 GitHub Actions 自动化发布流程。创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Build package
      run: uv build
    - name: Publish to PyPI
      run: uv publish
      env:
        UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

## 相关链接

- [uv 官方文档](https://docs.astral.sh/uv/)
- [PyPI 发布指南](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
