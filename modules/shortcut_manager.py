#!/usr/bin/env python3
"""
快捷方式管理模块
功能：查找、验证、清理桌面快捷方式
"""

import os
import struct
import shutil
from pathlib import Path


class ShortcutManager:
    """快捷方式管理器"""

    def __init__(self, desktop_path):
        """
        初始化快捷方式管理器

        Args:
            desktop_path: 桌面路径
        """
        self.desktop_path = Path(desktop_path)

    def find_shortcuts(self):
        """查找桌面上所有快捷方式"""
        shortcuts = []

        if not self.desktop_path.exists():
            return shortcuts

        for item in self.desktop_path.iterdir():
            if item.is_file() and item.suffix.lower() == ".lnk":
                info = self._parse_shortcut(item)
                info["name"] = item.stem
                info["path"] = str(item)
                info["valid"] = self._validate_shortcut(info)
                shortcuts.append(info)

        return shortcuts

    def _parse_shortcut(self, lnk_path):
        """解析 .lnk 快捷方式文件，提取目标路径"""
        info = {"target": "", "arguments": "", "icon": "", "description": ""}

        try:
            target = self._read_lnk_target(str(lnk_path))
            if target:
                info["target"] = target
        except Exception:
            pass

        try:
            # 尝试使用 pywin32 解析
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(lnk_path))
            info["target"] = shortcut.Targetpath
            info["arguments"] = getattr(shortcut, "Arguments", "")
            info["icon"] = getattr(shortcut, "IconLocation", "")
            info["description"] = getattr(shortcut, "Description", "")
        except ImportError:
            pass
        except Exception:
            pass

        return info

    def _read_lnk_target(self, lnk_path):
        """直接读取 .lnk 文件中的目标路径（不依赖 pywin32）"""
        try:
            with open(lnk_path, "rb") as f:
                data = f.read()

            # .lnk 文件头
            if len(data) < 76:
                return ""

            # 检查 CLSID
            if data[4:20] != b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46':
                return ""

            # 读取标志
            flags = struct.unpack('<I', data[20:24])[0]

            offset = 76  # 跳过文件头

            # 跳过目标列表
            if flags & 0x00000001:
                list_size = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2 + list_size

            # 跳过位置信息
            if flags & 0x00000002:
                offset += self._skip_string(data, offset, True)

            # 跳过描述
            if flags & 0x00000004:
                offset += self._skip_string(data, offset, False)

            # 跳过相对路径
            if flags & 0x00000008:
                offset += self._skip_string(data, offset, False)

            # 跳过工作目录
            if flags & 0x00000010:
                offset += self._skip_string(data, offset, False)

            # 跳过参数
            if flags & 0x00000020:
                offset += self._skip_string(data, offset, False)

            # 读取图标位置
            if flags & 0x00000040:
                icon_len = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2 + icon_len * 2

            # 读取环境变量块后的目标路径
            if flags & 0x00000200:
                # 读取环境变量块
                block_size = struct.unpack('<I', data[offset:offset+4])[0]
                offset += block_size

            # 尝试读取 Unicode 目标路径
            if flags & 0x00000080:
                # 使用 Unicode 字符串
                target = self._read_unicode_string(data, offset)
                if target:
                    return target

            # 回退：搜索路径字符串
            return self._search_for_path(data)

        except Exception:
            return ""

    @staticmethod
    def _skip_string(data, offset, is_unicode):
        """跳过一个字符串字段，返回跳过的字节数"""
        if is_unicode:
            length = struct.unpack('<H', data[offset:offset+2])[0]
            return 2 + length * 2
        else:
            length = struct.unpack('<H', data[offset:offset+2])[0]
            return 2 + length

    @staticmethod
    def _read_unicode_string(data, offset):
        """读取 Unicode 字符串"""
        try:
            length = struct.unpack('<H', data[offset:offset+2])[0]
            if length > 0 and offset + 2 + length * 2 <= len(data):
                return data[offset+2:offset+2+length*2].decode('utf-16-le', errors='ignore')
        except Exception:
            pass
        return ""

    @staticmethod
    def _search_for_path(data):
        """在 .lnk 文件中搜索路径字符串"""
        import re
        text = data.decode('utf-16-le', errors='ignore')
        # 匹配 Windows 路径
        patterns = [
            r'[A-Za-z]:\\[^\x00-\x1f"<>|]+',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        return ""

    def _validate_shortcut(self, info):
        """验证快捷方式目标是否存在"""
        target = info.get("target", "")
        if not target:
            return False
        return os.path.exists(target)

    def clean_invalid_shortcuts(self):
        """清理无效的快捷方式"""
        shortcuts = self.find_shortcuts()
        cleaned = 0

        for sc in shortcuts:
            if not sc["valid"]:
                try:
                    os.remove(sc["path"])
                    print(f"  [删除] {sc['name']}.lnk (目标不存在)")
                    cleaned += 1
                except Exception as e:
                    print(f"  [错误] 删除失败: {sc['name']} - {e}")

        return cleaned

    def create_shortcut(self, target_path, shortcut_name=None, description=""):
        """创建快捷方式"""
        if shortcut_name is None:
            shortcut_name = Path(target_path).stem

        shortcut_path = self.desktop_path / f"{shortcut_name}.lnk"

        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = str(Path(target_path).parent)
            shortcut.Description = description
            shortcut.save()
            print(f"  [创建] 快捷方式: {shortcut_name}")
            return True
        except ImportError:
            return self._create_shortcut_powershell(target_path, str(shortcut_path), description)
        except Exception as e:
            print(f"  [错误] 创建快捷方式失败: {e}")
            return False

    @staticmethod
    def _create_shortcut_powershell(target_path, shortcut_path, description=""):
        """使用 PowerShell 创建快捷方式"""
        import subprocess

        ps_script = f"""
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_path}"
        $Shortcut.Description = "{description}"
        $Shortcut.Save()
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print(f"  [创建] 快捷方式 (PowerShell)")
                return True
            else:
                print(f"  [错误] PowerShell: {result.stderr}")
                return False
        except Exception as e:
            print(f"  [错误] PowerShell 创建失败: {e}")
            return False

    def export_shortcut_list(self, output_file=None):
        """导出快捷方式列表"""
        shortcuts = self.find_shortcuts()

        if output_file is None:
            output_file = self.desktop_path / "shortcuts_list.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("  桌面快捷方式列表\n")
            f.write("=" * 60 + "\n\n")

            for i, sc in enumerate(shortcuts, 1):
                f.write(f"[{i}] {sc['name']}\n")
                f.write(f"    路径:   {sc['path']}\n")
                f.write(f"    目标:   {sc.get('target', 'N/A')}\n")
                f.write(f"    状态:   {'有效' if sc['valid'] else '无效'}\n")
                f.write("-" * 60 + "\n")

            f.write(f"\n共 {len(shortcuts)} 个快捷方式\n")
            f.write(f"有效: {sum(1 for s in shortcuts if s['valid'])}\n")
            f.write(f"无效: {sum(1 for s in shortcuts if not s['valid'])}\n")

        print(f"  [导出] 快捷方式列表已保存到: {output_file}")
        return output_file
