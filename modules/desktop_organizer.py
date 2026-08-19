#!/usr/bin/env python3
"""
桌面文件自动分类整理模块
按文件扩展名将桌面文件整理到对应文件夹中
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class DesktopOrganizer:
    """桌面文件分类整理器"""

    def __init__(self, desktop_path, rules, ignore_files=None, ignore_dirs=None):
        """
        初始化桌面整理器

        Args:
            desktop_path: 桌面路径
            rules: 分类规则 {文件夹名: [扩展名列表]}
            ignore_files: 忽略的文件名列表
            ignore_dirs: 忽略的目录名列表
        """
        self.desktop_path = Path(desktop_path)
        self.rules = rules
        self.ignore_files = ignore_files or []
        self.ignore_dirs = ignore_dirs or []
        self.stats = {
            "moved": 0,
            "skipped": 0,
            "dirs_created": 0,
            "details": {},
        }

    def _get_category(self, ext):
        """根据扩展名获取分类"""
        ext = ext.lower()
        for category, extensions in self.rules.items():
            if ext in [e.lower() for e in extensions]:
                return category
        return None

    def _ensure_dir(self, path):
        """确保目录存在"""
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self.stats["dirs_created"] += 1
            print(f"  [创建文件夹] {path.name}")

    def _handle_conflict(self, src, dst):
        """处理文件名冲突"""
        if not dst.exists():
            return dst

        stem = dst.stem
        suffix = dst.suffix
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_dst = dst.parent / new_name
            if not new_dst.exists():
                return new_dst
            counter += 1

    def organize(self):
        """执行桌面整理"""
        print(f"  扫描路径: {self.desktop_path}")
        print(f"  分类规则: {len(self.rules)} 类")

        for category in self.rules:
            self.stats["details"][category] = 0

        self.stats["details"]["Others"] = 0

        try:
            items = list(self.desktop_path.iterdir())
        except PermissionError:
            print("  [错误] 无权限访问桌面路径")
            return self.stats

        files = [f for f in items if f.is_file()]
        dirs = [d for d in items if d.is_dir()]

        print(f"  发现文件: {len(files)} 个, 文件夹: {len(dirs)} 个")
        print()

        for item in files:
            if item.name in self.ignore_files:
                self.stats["skipped"] += 1
                continue

            if item.name.startswith("."):
                self.stats["skipped"] += 1
                continue

            ext = item.suffix
            category = self._get_category(ext)

            if category is None:
                category = "Others"

            target_dir = self.desktop_path / category
            self._ensure_dir(target_dir)

            target_path = self._handle_conflict(item, target_dir / item.name)

            try:
                shutil.move(str(item), str(target_path))
                self.stats["moved"] += 1
                self.stats["details"][category] += 1
                print(f"  [移动] {item.name} -> {category}/")
            except Exception as e:
                print(f"  [错误] 移动失败: {item.name} - {e}")
                self.stats["skipped"] += 1

        print()
        return self.stats

    def undo_organize(self):
        """撤销整理 - 将分类文件夹中的文件移回桌面"""
        print("  [撤销整理] 正在恢复文件...")

        for category in list(self.rules.keys()) + ["Others"]:
            cat_dir = self.desktop_path / category
            if not cat_dir.exists():
                continue

            for item in cat_dir.iterdir():
                if item.is_file():
                    try:
                        target = self._handle_conflict(item, self.desktop_path / item.name)
                        shutil.move(str(item), str(target))
                        print(f"  [恢复] {category}/{item.name} -> 桌面")
                    except Exception as e:
                        print(f"  [错误] 恢复失败: {item.name} - {e}")

            try:
                if not any(cat_dir.iterdir()):
                    cat_dir.rmdir()
                    print(f"  [删除空文件夹] {category}")
            except Exception:
                pass

        print("  [完成] 撤销整理完成")

    def get_duplicates(self):
        """查找桌面上的重复文件（按文件大小和名称）"""
        import hashlib

        size_map = {}
        duplicates = []

        for item in self.desktop_path.iterdir():
            if not item.is_file():
                continue
            if item.name in self.ignore_files:
                continue

            try:
                size = item.stat().st_size
                if size == 0:
                    continue

                if size not in size_map:
                    size_map[size] = []
                size_map[size].append(item)
            except Exception:
                continue

        for size, files in size_map.items():
            if len(files) < 2:
                continue

            hash_map = {}
            for f in files:
                try:
                    h = hashlib.md5()
                    with open(f, "rb") as fh:
                        for chunk in iter(lambda: fh.read(8192), b""):
                            h.update(chunk)
                    file_hash = h.hexdigest()
                    if file_hash not in hash_map:
                        hash_map[file_hash] = []
                    hash_map[file_hash].append(f)
                except Exception:
                    continue

            for file_hash, dup_files in hash_map.items():
                if len(dup_files) > 1:
                    duplicates.append({
                        "hash": file_hash,
                        "size": size,
                        "files": [str(f) for f in dup_files],
                    })

        return duplicates
