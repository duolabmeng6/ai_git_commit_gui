# Git AI Commit - 智能提交助手

> 🤖 基于AI的Git提交消息生成工具，让代码提交更智能、更规范

## 📖 项目介绍

Git AI Commit 是一个现代化的Git提交助手，结合了AI技术和直观的图形界面，帮助开发者：

- 📊 **智能分析**：自动分析Git变更内容，生成结构化报告
- 🤖 **AI生成**：使用GLM-4-Flash模型生成规范的提交消息
- 🖥️ **图形界面**：提供友好的GUI界面，操作简单直观
- ⚙️ **灵活配置**：支持自定义API配置和个性化设置

## ✨ 功能特性

### 核心功能
- 🔍 **Git变更分析**：深度分析代码变更，识别修改、新增、删除的文件
- 📝 **智能提交消息**：基于变更内容生成符合规范的提交消息
- 🎯 **一键提交**：分析、生成、提交一站式完成
- 💾 **配置管理**：持久化保存API配置和用户偏好

### 界面特性
- 🎨 **现代化UI**：基于PySide6的原生界面，响应迅速
- 📱 **紧凑设计**：优化的窗口布局，节省屏幕空间
- 🔄 **异步处理**：多线程处理，避免界面卡顿
- 💡 **智能提示**：实时状态反馈和操作指导

## 🚀 快速开始

### 🎯 一键启动 (最简单)
```bash
# 安装uv并直接运行
curl -LsSf https://astral.sh/uv/install.sh | sh
uv run --from git+https://github.com/duolabmeng6/ai_git_commit_gui.git git-ai-commit
```

### 系统要求
- Python 3.12+
- Git (已安装并配置)
- 网络连接 (用于AI API调用)

### 安装方法

#### 使用 uv (推荐)

**方式1：直接从GitHub运行**
```bash
# 1. 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 直接运行项目
uv run --from git+https://github.com/duolabmeng6/ai_git_commit_gui.git git-ai-commit
```

**方式2：克隆后运行**
```bash
# 1. 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目
git clone https://github.com/duolabmeng6/ai_git_commit_gui.git
cd ai_git_commit_gui

# 3. 安装依赖
uv sync

# 4. 启动应用
uv run git-ai-commit
```

#### 传统方式

```bash
# 1. 克隆项目
git clone https://github.com/duolabmeng6/ai_git_commit_gui.git
cd ai_git_commit_gui

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -e .

# 4. 启动应用
python gui_main.py
```

## 📋 使用指南

### 首次配置

1. **启动应用**
   ```bash
   # 直接从GitHub启动
   uv run --from git+https://github.com/duolabmeng6/ai_git_commit_gui.git git-ai-commit

   # 或者如果已克隆项目
   uv run git-ai-commit
   ```

2. **配置API设置**
   - 切换到"设置"标签页
   - 输入API URL：`https://api.kenhong.com/v1`
   - 输入API密钥
   - 设置模型名称：`glm-4-flash`
   - 点击"保存设置"

3. **选择Git仓库**
   - 在"仓库路径"中输入或浏览选择Git仓库
   - 应用会自动验证仓库有效性

### 基本工作流程

1. **查看变更**：点击"查看变更信息"按钮，分析当前仓库的未提交变更
2. **AI分析**：点击"AI总结变更"按钮，生成智能提交消息
3. **执行提交**：确认提交消息后，点击"Git Commit"完成提交

### 命令行使用

```bash
# 分析指定仓库的变更
uv run python git_diff_analyzer.py /path/to/repo 200

# 启动GUI并指定仓库路径
uv run git-ai-commit /path/to/repo

# 使用当前目录
uv run git-ai-commit ./

# 直接启动GUI（会使用当前目录）
uv run python gui_main.py
```

### 使用示例

**场景1：分析当前项目变更**
```bash
cd /your/project/directory
uv run git-ai-commit ./
```

**场景2：快速查看变更内容**
```bash
uv run python git_diff_analyzer.py . 100
```

**场景3：AI生成提交消息**
1. 在GUI中点击"查看变更信息"
2. 查看分析结果
3. 点击"AI总结变更"
4. 确认生成的提交消息
5. 点击"Git Commit"完成提交

## ⚙️ 配置说明

### API配置
- **API URL**：AI服务的API端点地址
- **API Key**：访问AI服务的密钥
- **模型名称**：使用的AI模型，默认为 `glm-4-flash`

### 高级设置
配置文件位置：`~/.git_ai_commit/config.json`

```json
{
  "api": {
    "url": "https://api.kenhong.com/v1",
    "api_key": "your-api-key",
    "model": "glm-4-flash"
  },
  "ui": {
    "window_width": 400,
    "window_height": 550,
    "last_repo_path": ""
  },
  "git": {
    "max_diff_lines": 200,
    "auto_stage": false
  }
}
```

## 🛠️ 开发指南

### 项目结构
```
git_ai_commit/
├── gui_main.py          # GUI主界面
├── git_diff_analyzer.py # Git变更分析器
├── ai_interface.py      # AI接口模块
├── config.py           # 配置管理
├── utils.py            # 工具函数
├── pyproject.toml      # 项目配置
└── README.md           # 项目文档
```

### 开发环境设置
```bash
# 使用 uv 创建开发环境
uv sync --dev

# 运行测试
uv run python -m pytest

# 代码格式化
uv run black .
uv run isort .
```

## ❓ 常见问题

### Q: 如何获取API密钥？
A: 请联系API服务提供商获取有效的API密钥。确保密钥有足够的权限访问GLM-4-Flash模型。

### Q: 应用启动失败怎么办？
A: 请检查：
- Python版本是否为3.12+
- 是否正确安装了依赖：`uv sync`
- 是否在Git仓库目录中运行

### Q: AI分析失败怎么办？
A: 请检查：
- API密钥是否正确配置
- 网络连接是否正常
- API服务是否可用

### Q: 支持哪些Git操作？
A: 目前支持：
- 查看未提交的变更
- 生成提交消息
- 执行git add和git commit
- 不支持push操作（需手动执行）

## 🔧 故障排除

### 依赖安装问题
```bash
# 清理并重新安装
rm -rf .venv
uv sync

# 或使用传统方式
pip install --upgrade pip
pip install -e .
```

### GUI界面问题
- 确保系统支持Qt6
- 在Linux上可能需要安装额外的系统包：
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-pyside6

  # CentOS/RHEL
  sudo yum install python3-pyside6
  ```

### 配置文件问题
如果配置出现问题，可以删除配置文件重新开始：
```bash
rm -rf ~/.git_ai_commit/config.json
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至：developer@example.com

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
