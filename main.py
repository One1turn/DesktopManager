#!/usr/bin/env python3
"""
Windows 桌面美化整理工具
功能：桌面文件分类整理、壁纸轮换、系统状态监控、快捷方式管理
作者: Operit AI
日期: 2026-08-14
"""

import os
import sys
import json
import time
import shutil
import ctypes
import random
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# 导入自定义模块
from modules.desktop_organizer import DesktopOrganizer
from modules.wallpaper_manager import WallpaperManager
from modules.system_monitor import SystemMonitor
from modules.shortcut_manager import ShortcutManager


class DesktopManager:
    """Windows 桌面美化整理工具主程序"""

    VERSION = "1.0.0"
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / self.CONFIG_FILE
        self.config = self._load_config()

        print("=" * 60)
        print(f"  Windows 桌面美化整理工具 v{self.VERSION}")
        print(f"  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def _load_config(self):
        """加载配置文件"""
        default_config = {
            "desktop_path": str(Path.home() / "Desktop"),
            "wallpaper_folder": str(Path.home() / "Pictures" / "Wallpapers"),
            "wallpaper_interval": 300,
            "organize_rules": {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"],
                "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
                "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
                "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
                "Code": [".py", ".js", ".java", ".cpp", ".c", ".h", ".html", ".css", ".json", ".xml"],
            },
            "ignore_files": ["desktop.ini", "NTUSER.DAT"],
            "ignore_dirs": [],
            "monitor_interval": 5,
            "auto_organize": False,
            "auto_wallpaper": False,
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"[警告] 配置文件加载失败，使用默认配置: {e}")

        self._save_config(default_config)
        return default_config

    def _save_config(self, config):
        """保存配置文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[错误] 配置文件保存失败: {e}")

    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 60)
        print("  请选择功能:")
        print("-" * 60)
        print("  [1] 桌面文件分类整理")
        print("  [2] 壁纸管理 (随机切换壁纸)")
        print("  [3] 系统状态监控")
        print("  [4] 快捷方式管理")
        print("  [5] 自动美化模式 (整理+换壁纸)")
        print("  [6] 查看当前配置")
        print("  [7] 修改配置")
        print("  [8] 一键执行全部功能")
        print("  [0] 退出程序")
        print("=" * 60)

    def run(self):
        """主运行循环"""
        while True:
            self.show_menu()
            choice = input("\n请输入选项 [0-8]: ").strip()

            if choice == "0":
                print("\n感谢使用，再见！")
                break
            elif choice == "1":
                self._organize_desktop()
            elif choice == "2":
                self._manage_wallpaper()
            elif choice == "3":
                self._monitor_system()
            elif choice == "4":
                self._manage_shortcuts()
            elif choice == "5":
                self._auto_beautify()
            elif choice == "6":
                self._show_config()
            elif choice == "7":
                self._modify_config()
            elif choice == "8":
                self._run_all()
            else:
                print("[错误] 无效选项，请重新输入")

            input("\n按回车键继续...")

    def _organize_desktop(self):
        """桌面文件分类整理"""
        print("\n[桌面文件分类整理]")
        desktop_path = self.config["desktop_path"]

        if not os.path.exists(desktop_path):
            print(f"[错误] 桌面路径不存在: {desktop_path}")
            return

        organizer = DesktopOrganizer(
            desktop_path=desktop_path,
            rules=self.config["organize_rules"],
            ignore_files=self.config["ignore_files"],
            ignore_dirs=self.config["ignore_dirs"],
        )
        stats = organizer.organize()

        print(f"\n整理完成!")
        print(f"  移动文件数: {stats['moved']}")
        print(f"  跳过文件数: {stats['skipped']}")
        print(f"  创建文件夹数: {stats['dirs_created']}")
        for folder, count in stats["details"].items():
            if count > 0:
                print(f"    {folder}: {count} 个文件")

    def _manage_wallpaper(self):
        """壁纸管理"""
        print("\n[壁纸管理]")
        wallpaper_folder = self.config["wallpaper_folder"]

        if not os.path.exists(wallpaper_folder):
            print(f"[提示] 壁纸文件夹不存在，正在创建: {wallpaper_folder}")
            os.makedirs(wallpaper_folder, exist_ok=True)
            print("[提示] 请将壁纸图片放入该文件夹后重试")
            return

        manager = WallpaperManager(wallpaper_folder)
        images = manager.get_images()

        if not images:
            print("[提示] 未找到壁纸图片，请先添加图片到壁纸文件夹")
            print(f"  支持格式: .jpg .jpeg .png .bmp")
            return

        print(f"找到 {len(images)} 张壁纸图片")
        for i, img in enumerate(images, 1):
            print(f"  [{i}] {os.path.basename(img)}")

        print("\n[1] 随机切换壁纸")
        print("[2] 按序号选择壁纸")
        print("[3] 定时自动切换")
        sub_choice = input("请选择 [1-3]: ").strip()

        if sub_choice == "1":
            manager.set_random_wallpaper()
            print("[完成] 壁纸已随机切换")
        elif sub_choice == "2":
            idx = input(f"请输入序号 [1-{len(images)}]: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(images):
                    manager.set_wallpaper(images[idx])
                    print(f"[完成] 已设置壁纸: {os.path.basename(images[idx])}")
                else:
                    print("[错误] 序号超出范围")
            except ValueError:
                print("[错误] 请输入有效数字")
        elif sub_choice == "3":
            interval = input("切换间隔(秒) [默认300]: ").strip()
            interval = int(interval) if interval else 300
            print(f"[启动] 每 {interval} 秒自动切换壁纸 (Ctrl+C 停止)")
            manager.auto_rotate(interval)

    def _monitor_system(self):
        """系统状态监控"""
        print("\n[系统状态监控]")
        monitor = SystemMonitor()

        print("[1] 显示当前状态")
        print("[2] 持续监控 (Ctrl+C 停止)")
        sub_choice = input("请选择 [1-2]: ").strip()

        if sub_choice == "1":
            info = monitor.get_system_info()
            self._print_system_info(info)
        elif sub_choice == "2":
            interval = self.config["monitor_interval"]
            print(f"\n每 {interval} 秒刷新一次 (Ctrl+C 停止)\n")
            try:
                while True:
                    info = monitor.get_system_info()
                    self._print_system_info(info)
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[停止] 监控已停止")

    def _print_system_info(self, info):
        """打印系统信息"""
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 50)
        print("  系统状态监控")
        print(f"  时间: {info['time']}")
        print("=" * 50)
        print(f"  CPU 使用率:   {info['cpu_percent']:.1f}%")
        print(f"  内存使用率:   {info['memory_percent']:.1f}%")
        print(f"  内存总量:     {info['memory_total']:.1f} GB")
        print(f"  内存已用:     {info['memory_used']:.1f} GB")
        print(f"  磁盘使用率:   {info['disk_percent']:.1f}%")
        print(f"  磁盘总量:     {info['disk_total']:.1f} GB")
        print(f"  磁盘已用:     {info['disk_used']:.1f} GB")
        if "cpu_temp" in info:
            print(f"  CPU 温度:     {info['cpu_temp']}°C")
        print(f"  开机时长:     {info['uptime']}")
        print("=" * 50)

    def _manage_shortcuts(self):
        """快捷方式管理"""
        print("\n[快捷方式管理]")
        desktop_path = self.config["desktop_path"]
        manager = ShortcutManager(desktop_path)

        shortcuts = manager.find_shortcuts()
        print(f"找到 {len(shortcuts)} 个快捷方式")

        if not shortcuts:
            print("[提示] 桌面上没有找到快捷方式")
            return

        for i, sc in enumerate(shortcuts, 1):
            status = "有效" if sc["valid"] else "无效"
            print(f"  [{i}] {sc['name']} [{status}]")
            if sc["valid"]:
                print(f"      目标: {sc['target']}")

        print("\n[1] 清理无效快捷方式")
        print("[2] 查看快捷方式详情")
        print("[3] 返回")
        sub_choice = input("请选择 [1-3]: ").strip()

        if sub_choice == "1":
            cleaned = manager.clean_invalid_shortcuts()
            print(f"\n[完成] 清理了 {cleaned} 个无效快捷方式")
        elif sub_choice == "2":
            idx = input(f"请输入序号 [1-{len(shortcuts)}]: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(shortcuts):
                    sc = shortcuts[idx]
                    print(f"\n名称:   {sc['name']}")
                    print(f"路径:   {sc['path']}")
                    print(f"目标:   {sc.get('target', 'N/A')}")
                    print(f"状态:   {'有效' if sc['valid'] else '无效'}")
                else:
                    print("[错误] 序号超出范围")
            except ValueError:
                print("[错误] 请输入有效数字")

    def _auto_beautify(self):
        """自动美化模式"""
        print("\n[自动美化模式]")
        print("将执行以下操作:")
        print("  1. 整理桌面文件")
        print("  2. 随机切换壁纸")
        print("  3. 清理无效快捷方式")
        confirm = input("\n确认执行? (y/n): ").strip().lower()

        if confirm != "y":
            print("[取消] 操作已取消")
            return

        print("\n[1/3] 整理桌面文件...")
        self._organize_desktop()

        print("\n[2/3] 切换壁纸...")
        wallpaper_folder = self.config["wallpaper_folder"]
        if os.path.exists(wallpaper_folder):
            manager = WallpaperManager(wallpaper_folder)
            if manager.get_images():
                manager.set_random_wallpaper()
                print("[完成] 壁纸已切换")
            else:
                print("[跳过] 无可用壁纸")
        else:
            print("[跳过] 壁纸文件夹不存在")

        print("\n[3/3] 清理无效快捷方式...")
        desktop_path = self.config["desktop_path"]
        sc_manager = ShortcutManager(desktop_path)
        cleaned = sc_manager.clean_invalid_shortcuts()
        print(f"[完成] 清理了 {cleaned} 个无效快捷方式")

        print("\n[完成] 自动美化完成!")

    def _show_config(self):
        """显示当前配置"""
        print("\n[当前配置]")
        print(json.dumps(self.config, indent=2, ensure_ascii=False))

    def _modify_config(self):
        """修改配置"""
        print("\n[修改配置]")
        print("[1] 修改桌面路径")
        print("[2] 修改壁纸文件夹路径")
        print("[3] 修改壁纸切换间隔")
        print("[4] 修改监控刷新间隔")
        print("[5] 返回")

        choice = input("请选择 [1-5]: ").strip()

        if choice == "1":
            path = input(f"当前: {self.config['desktop_path']}\n新路径: ").strip()
            if path and os.path.exists(path):
                self.config["desktop_path"] = path
                self._save_config(self.config)
                print("[完成] 桌面路径已更新")
            else:
                print("[错误] 路径无效或不存在")
        elif choice == "2":
            path = input(f"当前: {self.config['wallpaper_folder']}\n新路径: ").strip()
            if path:
                self.config["wallpaper_folder"] = path
                self._save_config(self.config)
                print("[完成] 壁纸文件夹路径已更新")
        elif choice == "3":
            interval = input(f"当前: {self.config['wallpaper_interval']}秒\n新间隔(秒): ").strip()
            if interval.isdigit():
                self.config["wallpaper_interval"] = int(interval)
                self._save_config(self.config)
                print("[完成] 壁纸切换间隔已更新")
        elif choice == "4":
            interval = input(f"当前: {self.config['monitor_interval']}秒\n新间隔(秒): ").strip()
            if interval.isdigit():
                self.config["monitor_interval"] = int(interval)
                self._save_config(self.config)
                print("[完成] 监控刷新间隔已更新")

    def _run_all(self):
        """执行全部功能"""
        print("\n[一键执行全部功能]")
        self._organize_desktop()
        print()
        self._monitor_system()
        print()
        self._manage_shortcuts()
        print()
        wallpaper_folder = self.config["wallpaper_folder"]
        if os.path.exists(wallpaper_folder):
            manager = WallpaperManager(wallpaper_folder)
            if manager.get_images():
                manager.set_random_wallpaper()
                print("[完成] 壁纸已切换")
        print("\n[完成] 全部功能执行完毕!")


def check_admin():
    """检查是否有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    """程序入口"""
    try:
        app = DesktopManager()
        app.run()
    except KeyboardInterrupt:
        print("\n\n[中断] 程序已被用户中断")
    except Exception as e:
        print(f"\n[错误] 程序发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n程序已退出")


if __name__ == "__main__":
    main()
