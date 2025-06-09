#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供文件处理、编码检测、文本处理等工具函数
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
import re
import subprocess


def detect_file_encoding(file_path: str, fallback_encodings: List[str] = None) -> str:
    """
    检测文件编码
    
    Args:
        file_path: 文件路径
        fallback_encodings: 备用编码列表
    
    Returns:
        检测到的编码名称
    """
    if fallback_encodings is None:
        fallback_encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    try:
        # 使用chardet检测
        with open(file_path, 'rb') as f:
            raw_data = f.read(8192)  # 读取前8KB用于检测
            if raw_data:
                result = chardet.detect(raw_data)
                if result and result['encoding'] and result['confidence'] > 0.7:
                    return result['encoding']
    except (OSError, IOError):
        pass
    
    # 尝试备用编码
    for encoding in fallback_encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # 尝试读取一部分内容
            return encoding
        except (UnicodeDecodeError, OSError, IOError):
            continue
    
    return 'utf-8'  # 默认返回utf-8


def is_text_file(file_path: str, max_check_bytes: int = 8192) -> bool:
    """
    判断文件是否为文本文件
    
    Args:
        file_path: 文件路径
        max_check_bytes: 最大检查字节数
    
    Returns:
        是否为文本文件
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(max_check_bytes)
            if not chunk:
                return True  # 空文件视为文本文件
            
            # 检查是否包含null字节（二进制文件的特征）
            if b'\x00' in chunk:
                return False
            
            # 检查非打印字符的比例
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            non_text_count = sum(1 for byte in chunk if byte not in text_chars)
            
            # 如果非文本字符超过30%，认为是二进制文件
            if len(chunk) > 0 and (non_text_count / len(chunk)) > 0.30:
                return False
            
            return True
    
    except (OSError, IOError):
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    获取文件大小（MB）
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（MB）
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except (OSError, IOError):
        return 0.0


def safe_read_file(file_path: str, encoding: str = None, max_size_mb: float = 10.0) -> Optional[str]:
    """
    安全读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 指定编码，None时自动检测
        max_size_mb: 最大文件大小限制（MB）
    
    Returns:
        文件内容，读取失败时返回None
    """
    try:
        # 检查文件大小
        if get_file_size_mb(file_path) > max_size_mb:
            return f"[文件过大，超过{max_size_mb}MB限制]"
        
        # 检查是否为文本文件
        if not is_text_file(file_path):
            return "[二进制文件，无法显示内容]"
        
        # 检测编码
        if encoding is None:
            encoding = detect_file_encoding(file_path)
        
        # 读取文件
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            return f.read()
    
    except (OSError, IOError, UnicodeDecodeError) as e:
        return f"[读取文件失败: {str(e)}]"


def truncate_text_balanced(text: str, max_lines: int, 
                          deleted_marker: str = '-', 
                          added_marker: str = '+') -> str:
    """
    平衡截取文本内容，保持删除和新增内容的比例
    
    Args:
        text: 原始文本
        max_lines: 最大行数
        deleted_marker: 删除行标记
        added_marker: 新增行标记
    
    Returns:
        截取后的文本
    """
    if not text:
        return text
    
    lines = text.split('\n')
    if len(lines) <= max_lines:
        return text
    
    # 分类行
    deleted_lines = []
    added_lines = []
    context_lines = []
    
    for i, line in enumerate(lines):
        if line.startswith(deleted_marker) and not line.startswith('---'):
            deleted_lines.append((i, line))
        elif line.startswith(added_marker) and not line.startswith('+++'):
            added_lines.append((i, line))
        else:
            context_lines.append((i, line))
    
    # 保留所有上下文行
    result_lines = [line for _, line in context_lines]
    remaining_lines = max_lines - len(context_lines)
    
    if remaining_lines <= 0:
        return '\n'.join(result_lines[:max_lines])
    
    # 计算删除和新增行的分配
    total_change_lines = len(deleted_lines) + len(added_lines)
    if total_change_lines == 0:
        return '\n'.join(result_lines)
    
    # 按比例分配剩余行数
    deleted_ratio = len(deleted_lines) / total_change_lines
    deleted_quota = int(remaining_lines * deleted_ratio)
    added_quota = remaining_lines - deleted_quota
    
    # 确保至少各有一行（如果存在的话）
    if len(deleted_lines) > 0 and deleted_quota == 0:
        deleted_quota = 1
        added_quota = remaining_lines - 1
    if len(added_lines) > 0 and added_quota == 0:
        added_quota = 1
        deleted_quota = remaining_lines - 1
    
    # 截取删除行
    selected_deleted = deleted_lines[:deleted_quota]
    if len(deleted_lines) > deleted_quota:
        selected_deleted.append((-1, f"... (省略{len(deleted_lines) - deleted_quota}行删除内容)"))
    
    # 截取新增行
    selected_added = added_lines[:added_quota]
    if len(added_lines) > added_quota:
        selected_added.append((-1, f"... (省略{len(added_lines) - added_quota}行新增内容)"))
    
    # 合并所有行并按原始顺序排序
    all_selected = context_lines + selected_deleted + selected_added
    all_selected.sort(key=lambda x: x[0] if x[0] != -1 else float('inf'))
    
    return '\n'.join(line for _, line in all_selected)


def format_file_status(status: str) -> str:
    """
    格式化文件状态显示
    
    Args:
        status: Git文件状态
    
    Returns:
        格式化后的状态文本
    """
    status_map = {
        'modified': '修改',
        'added': '新增',
        'deleted': '删除',
        'untracked': '未跟踪',
        'renamed': '重命名',
        'copied': '复制',
        'updated': '更新',
        'unknown': '未知'
    }
    return status_map.get(status.lower(), status)


def clean_diff_output(diff_text: str) -> str:
    """
    清理diff输出，移除不必要的信息
    
    Args:
        diff_text: 原始diff文本
    
    Returns:
        清理后的diff文本
    """
    if not diff_text:
        return diff_text
    
    lines = diff_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 跳过diff头部信息（但保留文件路径信息）
        if line.startswith('diff --git'):
            continue
        elif line.startswith('index '):
            continue
        elif line.startswith('@@') and line.endswith('@@'):
            # 保留行号信息，但简化显示
            cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def extract_file_extension(file_path: str) -> str:
    """
    提取文件扩展名
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件扩展名（小写，包含点号）
    """
    return Path(file_path).suffix.lower()


def is_git_repository(path: str) -> bool:
    """
    检查路径是否为Git仓库
    
    Args:
        path: 要检查的路径
    
    Returns:
        是否为Git仓库
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def normalize_path(path: str) -> str:
    """
    规范化路径
    
    Args:
        path: 原始路径
    
    Returns:
        规范化后的路径
    """
    return str(Path(path).resolve())


def split_long_lines(text: str, max_line_length: int = 120) -> str:
    """
    分割过长的行
    
    Args:
        text: 原始文本
        max_line_length: 最大行长度
    
    Returns:
        处理后的文本
    """
    if not text:
        return text
    
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        if len(line) <= max_line_length:
            result_lines.append(line)
        else:
            # 对于过长的行，尝试在合适的位置分割
            while len(line) > max_line_length:
                # 寻找合适的分割点
                split_pos = max_line_length
                for i in range(max_line_length - 20, max_line_length):
                    if i < len(line) and line[i] in ' \t,;':
                        split_pos = i + 1
                        break
                
                result_lines.append(line[:split_pos])
                line = '  ' + line[split_pos:]  # 缩进续行
            
            if line.strip():  # 添加剩余部分
                result_lines.append(line)
    
    return '\n'.join(result_lines)


if __name__ == "__main__":
    # 测试工具函数
    print("测试工具函数...")
    
    # 测试当前目录
    current_dir = "."
    print(f"当前目录是否为Git仓库: {is_git_repository(current_dir)}")
    
    # 测试路径规范化
    test_path = "./test/../config.py"
    print(f"规范化路径: {normalize_path(test_path)}")
    
    # 测试文本截取
    test_text = "\n".join([f"- 删除行 {i}" for i in range(10)] + 
                         [f"+ 新增行 {i}" for i in range(15)])
    truncated = truncate_text_balanced(test_text, 10)
    print(f"截取后行数: {len(truncated.split(chr(10)))}")
    
    print("工具函数测试完成")
