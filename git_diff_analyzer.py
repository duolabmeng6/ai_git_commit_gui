#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git差异分析器
用于读取本地Git仓库的未提交文件变更，并整理成适合AI总结的格式
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional


class GitDiffAnalyzer:
    """Git差异分析器类"""
    
    def __init__(self, repo_path: str, max_lines: int = 200):
        """
        初始化分析器
        
        Args:
            repo_path: Git仓库路径
            max_lines: 最大显示行数限制
        """
        self.repo_path = Path(repo_path).resolve()
        self.max_lines = max_lines
        self.binary_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.dll', '.so',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv'
        }
    
    def validate_repo(self) -> bool:
        """验证是否为有效的Git仓库"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def is_binary_file(self, file_path: str) -> bool:
        """判断是否为二进制文件"""
        # 通过扩展名判断
        ext = Path(file_path).suffix.lower()
        if ext in self.binary_extensions:
            return True
        
        # 通过Git判断
        try:
            result = subprocess.run(
                ['git', 'diff', '--numstat', 'HEAD', '--', file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                # Git numstat输出格式: additions deletions filename
                # 二进制文件显示为: - - filename
                parts = result.stdout.strip().split('\t')
                if len(parts) >= 2 and parts[0] == '-' and parts[1] == '-':
                    return True
        except subprocess.CalledProcessError:
            pass
        
        return False
    
    def get_unstaged_files(self) -> List[Dict[str, str]]:
        """获取未暂存的文件列表"""
        try:
            # 获取工作区状态
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                status = line[:2]
                # Git status格式: XY filename，其中XY是两个字符的状态，后面跟一个空格
                file_path = line[2:].strip() if len(line) > 2 else line.strip()
                
                # 解析文件状态
                file_status = 'unknown'
                if status[0] == 'M' or status[1] == 'M':
                    file_status = 'modified'
                elif status[0] == 'A' or status[1] == 'A':
                    file_status = 'added'
                elif status[0] == 'D' or status[1] == 'D':
                    file_status = 'deleted'
                elif status[0] == '?' and status[1] == '?':
                    file_status = 'untracked'
                elif status[0] == 'R':
                    file_status = 'renamed'
                
                files.append({
                    'path': file_path,
                    'status': file_status,
                    'is_binary': self.is_binary_file(file_path) if file_status != 'deleted' else False
                })
            
            return files
        
        except subprocess.CalledProcessError as e:
            raise Exception(f"获取文件状态失败: {e}")
    
    def get_file_diff(self, file_path: str, file_status: str) -> Optional[str]:
        """获取文件的差异内容"""
        try:
            if file_status == 'untracked':
                # 新文件，显示全部内容
                full_path = self.repo_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        return f"+++ 新增文件内容 +++\n{content}"
                    except UnicodeDecodeError:
                        return "+++ 新增文件 (二进制或编码问题) +++"
                return None
            
            elif file_status == 'deleted':
                # 删除的文件，显示原内容
                result = subprocess.run(
                    ['git', 'show', f'HEAD:{file_path}'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return f"--- 删除文件内容 ---\n{result.stdout}"
                return "--- 删除文件 (无法获取原内容) ---"
            
            else:
                # 修改的文件，获取diff
                result = subprocess.run(
                    ['git', 'diff', 'HEAD', '--', file_path],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout:
                    return result.stdout
                
                # 如果没有与HEAD的diff，可能是暂存区的变更
                result = subprocess.run(
                    ['git', 'diff', '--', file_path],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return result.stdout
        
        except subprocess.CalledProcessError:
            pass
        
        return None

    def clean_diff_content(self, diff_content: str) -> str:
        """清理diff内容，移除空行"""
        if not diff_content:
            return diff_content

        lines = diff_content.split('\n')
        cleaned_lines = []

        for line in lines:
            # 跳过完全空白的行
            if line.strip() == '':
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def truncate_diff_content(self, diff_content: str) -> str:
        """截取diff内容，保持删除和新增内容的平衡"""
        if not diff_content:
            return diff_content
        
        lines = diff_content.split('\n')
        if len(lines) <= self.max_lines:
            return diff_content
        
        # 分离删除行和新增行
        deleted_lines = []
        added_lines = []
        context_lines = []
        
        for line in lines:
            if line.startswith('-') and not line.startswith('---'):
                deleted_lines.append(line)
            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line)
            else:
                context_lines.append(line)
        
        # 计算可用行数（减去上下文行）
        available_lines = self.max_lines - len(context_lines)
        if available_lines <= 0:
            return '\n'.join(context_lines[:self.max_lines])
        
        # 删除和新增各占一半
        half_lines = available_lines // 2
        
        truncated_deleted = deleted_lines[:half_lines]
        truncated_added = added_lines[:half_lines]
        
        # 重新组合
        result_lines = context_lines.copy()
        
        # 插入截取的删除行
        if truncated_deleted:
            if len(deleted_lines) > half_lines:
                truncated_deleted.append(f"... (省略{len(deleted_lines) - half_lines}行删除内容)")
            result_lines.extend(truncated_deleted)
        
        # 插入截取的新增行
        if truncated_added:
            if len(added_lines) > half_lines:
                truncated_added.append(f"... (省略{len(added_lines) - half_lines}行新增内容)")
            result_lines.extend(truncated_added)
        
        return '\n'.join(result_lines)
    
    def analyze_repository(self) -> Dict:
        """分析仓库并返回格式化结果"""
        if not self.validate_repo():
            raise Exception(f"路径 '{self.repo_path}' 不是有效的Git仓库")
        
        files = self.get_unstaged_files()
        
        # 统计信息
        stats = {
            'modified': 0,
            'added': 0,
            'deleted': 0,
            'untracked': 0,
            'renamed': 0
        }
        
        file_details = []
        
        for file_info in files:
            file_path = file_info['path']
            file_status = file_info['status']
            is_binary = file_info['is_binary']
            
            stats[file_status] = stats.get(file_status, 0) + 1
            
            detail = {
                'path': file_path,
                'status': file_status,
                'is_binary': is_binary,
                'diff_content': None
            }
            
            if is_binary:
                detail['diff_content'] = f"二进制文件: {file_path}"
            else:
                diff_content = self.get_file_diff(file_path, file_status)
                if diff_content:
                    detail['diff_content'] = self.truncate_diff_content(diff_content)
            
            file_details.append(detail)
        
        return {
            'repo_path': str(self.repo_path),
            'stats': stats,
            'files': file_details,
            'total_files': len(files)
        }
    
    def format_output(self, analysis_result: Dict) -> str:
        """格式化输出结果"""
        output = []
        
        # 仓库信息
        output.append(f"仓库路径: {analysis_result['repo_path']}")
        output.append("")
        
        # 变更摘要
        stats = analysis_result['stats']
        summary_parts = []
        if stats.get('modified', 0) > 0:
            summary_parts.append(f"{stats['modified']}个文件修改")
        if stats.get('added', 0) > 0:
            summary_parts.append(f"{stats['added']}个文件新增")
        if stats.get('untracked', 0) > 0:
            summary_parts.append(f"{stats['untracked']}个文件未跟踪")
        if stats.get('deleted', 0) > 0:
            summary_parts.append(f"{stats['deleted']}个文件删除")
        if stats.get('renamed', 0) > 0:
            summary_parts.append(f"{stats['renamed']}个文件重命名")
        
        if summary_parts:
            output.append(f"变更摘要: {', '.join(summary_parts)}")
        else:
            output.append("变更摘要: 无未提交的变更")
        
        output.append("")
        output.append("=" * 50)
        output.append("文件变更详情")
        output.append("=" * 50)
        
        # 文件详情
        for file_detail in analysis_result['files']:
            output.append("")
            status_map = {
                'modified': '修改',
                'added': '新增',
                'deleted': '删除',
                'untracked': '未跟踪',
                'renamed': '重命名'
            }
            status_text = status_map.get(file_detail['status'], file_detail['status'])
            output.append(f"文件: {file_detail['path']} ({status_text})")
            
            if file_detail['is_binary']:
                output.append("类型: 二进制文件")
            elif file_detail['diff_content']:
                output.append("变更内容:")
                output.append("-" * 30)
                # 清理空行后再显示
                cleaned_content = self.clean_diff_content(file_detail['diff_content'])
                output.append(cleaned_content)
                output.append("-" * 30)
        
        return '\n'.join(output)


if __name__ == "__main__":
    # 命令行测试
    if len(sys.argv) < 2:
        print("用法: python git_diff_analyzer.py <仓库路径> [最大行数]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    max_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    
    try:
        analyzer = GitDiffAnalyzer(repo_path, max_lines)
        result = analyzer.analyze_repository()
        formatted_output = analyzer.format_output(result)
        print(formatted_output)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
