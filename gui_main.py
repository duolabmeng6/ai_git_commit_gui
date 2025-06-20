#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git AI Commit GUI主界面
提供图形化界面来管理Git变更分析和AI提交消息生成
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QFormLayout, QSplitter, QGroupBox, QProgressBar, QGridLayout
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from config import config_manager
from git_diff_analyzer import GitDiffAnalyzer
from ai_interface import create_ai_interface
from utils import is_git_repository, normalize_path


class GitAnalysisWorker(QThread):
    """Git分析工作线程"""
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, repo_path: str, max_lines: int = 200):
        super().__init__()
        self.repo_path = repo_path
        self.max_lines = max_lines
    
    def run(self):
        try:
            analyzer = GitDiffAnalyzer(self.repo_path, self.max_lines)
            result = analyzer.analyze_repository()
            formatted_output = analyzer.format_output(result)
            self.finished.emit(formatted_output)
        except Exception as e:
            self.error.emit(str(e))


class AIAnalysisWorker(QThread):
    """AI分析工作线程"""
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, git_analysis: str, api_config: dict):
        super().__init__()
        self.git_analysis = git_analysis
        self.api_config = api_config
    
    def run(self):
        try:
            ai = create_ai_interface(
                self.api_config["api_key"],
                self.api_config["url"],
                self.api_config["model"]
            )
            # 使用自定义提示词（如果有的话）
            custom_prompt = self.api_config.get("prompt", "").strip()
            result = ai.generate_commit_message(
                self.git_analysis,
                custom_prompt if custom_prompt else None
            )
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("AI分析失败：未返回结果")
        except Exception as e:
            self.error.emit(f"AI分析失败：{str(e)}")


class GitAnalyzerGUI(QMainWindow):
    """Git分析器主界面"""

    def __init__(self, repo_path: str = "./", auto_mode: bool = False):
        super().__init__()
        self.current_repo_path = ""
        self.git_analysis_result = ""
        self.initial_repo_path = repo_path
        self.auto_mode = auto_mode

        # 工作线程
        self.git_worker = None
        self.ai_worker = None

        # 自动流程状态管理
        self.auto_process_state = "IDLE"  # IDLE, GIT_ANALYSIS, AI_ANALYSIS, COMMIT

        self.init_ui()
        self.load_settings()
        self.setup_auto_path()

        # 如果是自动模式，设置定时器自动执行
        if self.auto_mode:
            self.setup_auto_execution()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Git AI Commit - 智能提交助手 微信:261077")
        self.setMinimumSize(400, 500)  # 减小最小窗口尺寸
        self.resize(400, 550)  # 设置默认窗口大小
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 仓库路径选择区域
        self.create_repo_selection_area(main_layout)
        
        # 创建标签页
        self.create_tab_widget(main_layout)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_repo_selection_area(self, parent_layout):
        """创建仓库选择区域"""
        repo_group = QGroupBox("仓库选择")
        repo_layout = QHBoxLayout(repo_group)
        
        # 路径输入框
        self.repo_path_edit = QLineEdit()
        self.repo_path_edit.setPlaceholderText("请选择Git仓库路径...")
        self.repo_path_edit.textChanged.connect(self.on_repo_path_changed)
        
        # 浏览按钮
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_repo_path)
        
        repo_layout.addWidget(QLabel("仓库路径:"))
        repo_layout.addWidget(self.repo_path_edit)
        repo_layout.addWidget(browse_btn)
        
        parent_layout.addWidget(repo_group)
    
    def create_tab_widget(self, parent_layout):
        """创建标签页部件"""
        self.tab_widget = QTabWidget()
        
        # 代码标签页
        self.create_code_tab()
        
        # 设置标签页
        self.create_settings_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_code_tab(self):
        """创建代码标签页"""
        code_widget = QWidget()
        code_layout = QVBoxLayout(code_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()

        self.view_changes_btn = QPushButton("查看变更信息")
        self.view_changes_btn.clicked.connect(self.view_git_changes)

        self.ai_summary_btn = QPushButton("AI总结变更")
        self.ai_summary_btn.clicked.connect(self.ai_analyze_changes)

        self.commit_btn = QPushButton("Git Commit")
        self.commit_btn.clicked.connect(self.git_commit)
        self.commit_btn.setEnabled(False)

        self.auto_process_btn = QPushButton("一键处理")
        self.auto_process_btn.clicked.connect(self.auto_process)
        self.auto_process_btn.setEnabled(False)

        button_layout.addWidget(self.view_changes_btn)
        button_layout.addWidget(self.ai_summary_btn)
        button_layout.addWidget(self.commit_btn)
        button_layout.addWidget(self.auto_process_btn)

        code_layout.addLayout(button_layout)
        
        # 文本显示区域（改为上下布局）
        # Git变更信息文本框
        changes_group = QGroupBox("Git变更信息")
        changes_layout = QVBoxLayout(changes_group)
        self.changes_text = QTextEdit()
        self.changes_text.setFont(QFont("Monaco", 9))  # 使用系统等宽字体，减小字号
        self.changes_text.setPlaceholderText("点击'查看变更信息'按钮查看Git变更...")
        self.changes_text.setMaximumHeight(200)  # 限制高度
        changes_layout.addWidget(self.changes_text)

        # AI分析结果文本框
        ai_group = QGroupBox("AI分析结果")
        ai_layout = QVBoxLayout(ai_group)
        self.ai_result_text = QTextEdit()
        self.ai_result_text.setFont(QFont("Monaco", 9))  # 使用系统等宽字体，减小字号
        self.ai_result_text.setPlaceholderText("点击'AI总结变更'按钮获取AI分析...")
        self.ai_result_text.setMaximumHeight(150)  # 限制高度，AI结果通常较短
        ai_layout.addWidget(self.ai_result_text)

        code_layout.addWidget(changes_group)
        code_layout.addWidget(ai_group)
        
        self.tab_widget.addTab(code_widget, "代码")
    
    def create_settings_tab(self):
        """创建设置标签页"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(20)

        # API设置组
        api_group = QGroupBox("OpenAI API 设置")
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(15)

        # 使用网格布局来更好地控制宽度
        api_grid = QGridLayout()
        api_grid.setColumnStretch(1, 1)  # 让第二列（输入框）可以拉伸

        # API URL
        api_url_label = QLabel("API URL:")
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("https://api.kenhong.com/v1")
        self.api_url_edit.setMinimumWidth(300)
        api_grid.addWidget(api_url_label, 0, 0)
        api_grid.addWidget(self.api_url_edit, 0, 1)

        # API Key
        api_key_label = QLabel("API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("请输入API密钥...")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setMinimumWidth(300)
        api_grid.addWidget(api_key_label, 1, 0)
        api_grid.addWidget(self.api_key_edit, 1, 1)

        # 模型名称
        model_label = QLabel("模型名称:")
        self.model_name_edit = QLineEdit()
        self.model_name_edit.setPlaceholderText("glm-4-flash")
        self.model_name_edit.setMinimumWidth(300)
        api_grid.addWidget(model_label, 2, 0)
        api_grid.addWidget(self.model_name_edit, 2, 1)

        api_layout.addLayout(api_grid)

        # 提示词设置
        prompt_label = QLabel("AI提示词:")
        prompt_label.setAlignment(Qt.AlignTop)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("请输入AI生成提交消息的提示词...")
        self.prompt_edit.setMaximumHeight(120)  # 限制高度
        self.prompt_edit.setMinimumHeight(80)   # 最小高度

        # 创建提示词的网格布局
        prompt_grid = QGridLayout()
        prompt_grid.addWidget(prompt_label, 0, 0)
        prompt_grid.addWidget(self.prompt_edit, 0, 1)
        prompt_grid.setColumnStretch(1, 1)  # 让文本框可以拉伸

        api_layout.addLayout(prompt_grid)

        # 保存按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        save_btn = QPushButton("保存设置")
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()

        settings_layout.addWidget(api_group)
        settings_layout.addLayout(button_layout)
        settings_layout.addStretch()

        self.tab_widget.addTab(settings_widget, "设置")
    
    def setup_auto_path(self):
        """自动设置路径"""
        current_dir = os.getcwd()

        # 使用传入的路径参数
        input_path = self.initial_repo_path
        # 如果是相对路径"./"，转换为绝对路径
        if input_path == "./":
            resolved_path = normalize_path(current_dir)
        else:
            resolved_path = normalize_path(input_path)

        # 设置路径
        self.repo_path_edit.setText(resolved_path)
        self.current_repo_path = resolved_path

    def setup_auto_execution(self):
        """设置自动执行"""
        # 使用定时器延迟执行，确保GUI完全初始化
        self.auto_timer = QTimer()
        self.auto_timer.setSingleShot(True)
        self.auto_timer.timeout.connect(self.auto_execute)
        self.auto_timer.start(1000)  # 1秒后执行

    def auto_execute(self):
        """自动执行一键处理"""
        print(f"自动模式：开始检查仓库路径: {self.current_repo_path}")

        # 检查仓库路径是否有效
        if not self.current_repo_path or not is_git_repository(self.current_repo_path):
            print(f"错误：无效的Git仓库路径: {self.current_repo_path}")
            QApplication.quit()
            return

        print("自动模式：仓库路径有效，检查API配置...")

        # 检查API配置
        api_config = config_manager.get_api_config()
        if not api_config["api_key"]:
            print("错误：未配置API密钥，请先在设置中配置")
            QApplication.quit()
            return

        print("开始自动执行一键处理...")
        # 触发自动处理
        self.auto_process()

    def load_settings(self):
        """加载设置"""
        # 加载API设置
        api_config = config_manager.get_api_config()
        self.api_url_edit.setText(api_config["url"])
        self.api_key_edit.setText(api_config["api_key"])
        self.model_name_edit.setText(api_config["model"])
        self.prompt_edit.setPlainText(api_config["prompt"])

        # 加载UI设置
        ui_config = config_manager.get_ui_config()
        self.resize(ui_config["window_width"], ui_config["window_height"])

        # 加载上次的仓库路径
        last_repo = ui_config["last_repo_path"]
        if last_repo and not self.current_repo_path:
            self.repo_path_edit.setText(last_repo)
            self.current_repo_path = last_repo

    def save_settings(self):
        """保存设置"""
        # 保存API设置
        config_manager.set_api_config(
            self.api_url_edit.text().strip(),
            self.api_key_edit.text().strip(),
            self.model_name_edit.text().strip(),
            self.prompt_edit.toPlainText().strip()
        )

        # 保存UI设置
        config_manager.set_ui_config(
            window_width=self.width(),
            window_height=self.height(),
            last_repo_path=self.current_repo_path
        )

        QMessageBox.information(self, "设置", "设置已保存")

    def browse_repo_path(self):
        """浏览仓库路径"""
        current_path = self.repo_path_edit.text() or os.getcwd()
        repo_path = QFileDialog.getExistingDirectory(
            self, "选择Git仓库", current_path
        )

        if repo_path:
            self.repo_path_edit.setText(repo_path)

    def on_repo_path_changed(self, path: str):
        """仓库路径改变时的处理"""
        self.current_repo_path = path.strip()

        # 检查是否为有效的Git仓库
        if self.current_repo_path and is_git_repository(self.current_repo_path):
            self.statusBar().showMessage(f"Git仓库: {self.current_repo_path}")
            self.view_changes_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)
        else:
            self.statusBar().showMessage("请选择有效的Git仓库")
            self.view_changes_btn.setEnabled(False)
            self.ai_summary_btn.setEnabled(False)
            self.commit_btn.setEnabled(False)
            self.auto_process_btn.setEnabled(False)

    def view_git_changes(self):
        """查看Git变更"""
        if not self.current_repo_path:
            QMessageBox.warning(self, "警告", "请先选择Git仓库路径")
            return

        if not is_git_repository(self.current_repo_path):
            QMessageBox.warning(self, "警告", "选择的路径不是有效的Git仓库")
            return

        # 禁用按钮，显示进度
        self.view_changes_btn.setEnabled(False)
        self.statusBar().showMessage("正在分析Git变更...")

        # 启动Git分析工作线程
        git_config = config_manager.get_git_config()
        self.git_worker = GitAnalysisWorker(
            self.current_repo_path,
            git_config["max_diff_lines"]
        )
        self.git_worker.finished.connect(self.on_git_analysis_finished)
        self.git_worker.error.connect(self.on_git_analysis_error)
        self.git_worker.start()

    def on_git_analysis_finished(self, result: str):
        """Git分析完成"""
        self.git_analysis_result = result
        self.changes_text.setPlainText(result)

        # 检查是否在自动流程中
        if self.auto_process_state == "GIT_ANALYSIS":
            # 自动流程：继续AI分析
            self.auto_process_state = "AI_ANALYSIS"
            self.statusBar().showMessage("一键处理：正在进行AI分析...")
            self.ai_analyze_changes()
        else:
            # 手动操作：恢复按钮状态
            self.view_changes_btn.setEnabled(True)
            self.ai_summary_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)
            self.statusBar().showMessage("Git变更分析完成")

    def on_git_analysis_error(self, error: str):
        """Git分析错误"""
        # 重置自动流程状态
        if self.auto_process_state != "IDLE":
            self.auto_process_state = "IDLE"
            self.statusBar().showMessage("一键处理失败：Git变更分析失败")

            # 如果是自动模式，打印错误并退出
            if self.auto_mode:
                print(f"自动处理失败：Git变更分析失败: {error}")
                QApplication.quit()
                return
        else:
            self.statusBar().showMessage("Git变更分析失败")

        # 恢复按钮状态
        self.view_changes_btn.setEnabled(True)
        self.ai_summary_btn.setEnabled(False)
        self.commit_btn.setEnabled(False)
        self.auto_process_btn.setEnabled(True)

        QMessageBox.critical(self, "错误", f"Git分析失败：{error}")

    def ai_analyze_changes(self):
        """AI分析变更"""
        if not self.git_analysis_result:
            QMessageBox.warning(self, "警告", "请先查看Git变更信息")
            return

        # 检查API配置
        api_config = config_manager.get_api_config()
        if not api_config["api_key"]:
            QMessageBox.warning(self, "警告", "请先在设置中配置API密钥")
            self.tab_widget.setCurrentIndex(1)  # 切换到设置标签页
            return

        # 禁用按钮，显示进度
        self.ai_summary_btn.setEnabled(False)
        self.statusBar().showMessage("正在进行AI分析...")

        # 启动AI分析工作线程
        self.ai_worker = AIAnalysisWorker(self.git_analysis_result, api_config)
        self.ai_worker.finished.connect(self.on_ai_analysis_finished)
        self.ai_worker.error.connect(self.on_ai_analysis_error)
        self.ai_worker.start()

    def on_ai_analysis_finished(self, result: str):
        """AI分析完成"""
        self.ai_result_text.setPlainText(result)

        # 检查是否在自动流程中
        if self.auto_process_state == "AI_ANALYSIS":
            # 自动流程：继续Git提交
            self.auto_process_state = "COMMIT"
            self.statusBar().showMessage("一键处理：正在执行Git提交...")
            self.git_commit()
        else:
            # 手动操作：恢复按钮状态
            self.ai_summary_btn.setEnabled(True)
            self.commit_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)
            self.statusBar().showMessage("AI分析完成")

    def on_ai_analysis_error(self, error: str):
        """AI分析错误"""
        # 重置自动流程状态
        if self.auto_process_state != "IDLE":
            self.auto_process_state = "IDLE"
            self.statusBar().showMessage("一键处理失败：AI分析失败")

            # 如果是自动模式，打印错误并退出
            if self.auto_mode:
                print(f"自动处理失败：AI分析失败: {error}")
                QApplication.quit()
                return
        else:
            self.statusBar().showMessage("AI分析失败")

        # 恢复按钮状态
        self.view_changes_btn.setEnabled(True)
        self.ai_summary_btn.setEnabled(True)
        self.commit_btn.setEnabled(False)
        self.auto_process_btn.setEnabled(True)

        QMessageBox.critical(self, "错误", f"AI分析失败：{error}")

    def auto_process(self):
        """一键处理：自动执行查看变更→AI分析→Git提交"""
        # 检查仓库路径
        if not self.current_repo_path:
            QMessageBox.warning(self, "警告", "请先选择Git仓库路径")
            return

        if not is_git_repository(self.current_repo_path):
            QMessageBox.warning(self, "警告", "选择的路径不是有效的Git仓库")
            return

        # 检查API配置
        api_config = config_manager.get_api_config()
        if not api_config["api_key"]:
            QMessageBox.warning(self, "警告", "请先在设置中配置API密钥")
            self.tab_widget.setCurrentIndex(1)  # 切换到设置标签页
            return

        # 开始自动流程
        self.auto_process_state = "GIT_ANALYSIS"
        self.statusBar().showMessage("一键处理：正在分析Git变更...")

        # 禁用所有按钮
        self.view_changes_btn.setEnabled(False)
        self.ai_summary_btn.setEnabled(False)
        self.commit_btn.setEnabled(False)
        self.auto_process_btn.setEnabled(False)

        # 启动Git分析
        self.view_git_changes()

    def git_commit(self):
        """执行Git提交"""
        if not self.current_repo_path:
            QMessageBox.warning(self, "警告", "请先选择Git仓库路径")
            return

        commit_message = self.ai_result_text.toPlainText().strip()
        if not commit_message:
            QMessageBox.warning(self, "警告", "没有提交消息")
            return

        try:
            # 执行git add .
            subprocess.run(
                ["git", "add", "."],
                cwd=self.current_repo_path,
                check=True
            )

            # 执行git commit
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.current_repo_path,
                check=True
            )

            # 检查是否在自动流程中
            if self.auto_process_state == "COMMIT":
                self.statusBar().showMessage("一键处理完成：Git提交成功")
                self.auto_process_state = "IDLE"

                # 如果是自动模式，完成后自动关闭
                if self.auto_mode:
                    print("自动处理完成：Git提交成功")
                    QApplication.quit()
                    return
            else:
                self.statusBar().showMessage("Git提交成功")

            # 清空文本框
            self.changes_text.clear()
            self.ai_result_text.clear()
            self.git_analysis_result = ""

            # 恢复按钮状态
            self.view_changes_btn.setEnabled(True)
            self.ai_summary_btn.setEnabled(False)
            self.commit_btn.setEnabled(False)
            self.auto_process_btn.setEnabled(True)

        except subprocess.CalledProcessError as e:
            # 重置自动流程状态
            if self.auto_process_state != "IDLE":
                self.auto_process_state = "IDLE"
                self.statusBar().showMessage("一键处理失败：Git提交失败")

                # 如果是自动模式，打印错误并退出
                if self.auto_mode:
                    print(f"自动处理失败：Git提交失败: {e}")
                    QApplication.quit()
                    return
            else:
                self.statusBar().showMessage("Git提交失败")

            # 恢复按钮状态
            self.view_changes_btn.setEnabled(True)
            self.ai_summary_btn.setEnabled(True)
            self.commit_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)

            QMessageBox.critical(self, "错误", f"Git提交失败：{e}")
        

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存窗口大小和位置
        config_manager.set_ui_config(
            window_width=self.width(),
            window_height=self.height(),
            last_repo_path=self.current_repo_path
        )
        event.accept()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Git AI Commit - 智能提交助手")
    parser.add_argument("repo_path", nargs="?", default="./",
                       help="Git仓库路径 (默认: 当前目录)")
    parser.add_argument("--auto", action="store_true",
                       help="自动执行一键处理并关闭窗口")
    args = parser.parse_args()

    # 创建QApplication时只传递程序名，避免Qt解析我们的自定义参数
    app = QApplication([sys.argv[0]])
    app.setApplicationName("Git AI Commit")
    app.setApplicationVersion("1.0.0")

    # 创建主窗口，传入解析的参数
    window = GitAnalyzerGUI(repo_path=args.repo_path, auto_mode=args.auto)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
