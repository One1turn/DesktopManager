#!/usr/bin/env python3
"""
壁纸管理模块
功能：随机切换壁纸、定时轮换、下载壁纸
"""

import os
import sys
import time
import random
import ctypes
import threading
from pathlib import Path


class WallpaperManager:
    """壁纸管理器"""

    SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

    def __init__(self, wallpaper_folder):
        """
        初始化壁纸管理器

        Args:
            wallpaper_folder: 壁纸图片文件夹路径
        """
        self.folder = Path(wallpaper_folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self._stop_flag = False
        self._thread = None

    def get_images(self):
        """获取文件夹中所有支持的图片文件"""
        if not self.folder.exists():
            return []

        images = []
        for item in self.folder.iterdir():
            if item.is_file() and item.suffix.lower() in self.SUPPORTED_FORMATS:
                images.append(str(item))

        images.sort()
        return images

    def set_wallpaper(self, image_path):
        """
        设置桌面壁纸

        Args:
            image_path: 图片文件路径
        """
        if not os.path.exists(image_path):
            print(f"  [错误] 图片文件不存在: {image_path}")
            return False

        try:
            # Windows API 设置壁纸
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02

            result = ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                str(image_path),
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
            )

            if result:
                return True
            else:
                print(f"  [错误] 设置壁纸失败，错误码: {ctypes.get_last_error()}")
                return False
        except AttributeError:
            # 非 Windows 系统
            self._set_wallpaper_linux(image_path)
            return True
        except Exception as e:
            print(f"  [错误] 设置壁纸异常: {e}")
            return False

    def _set_wallpaper_linux(self, image_path):
        """Linux 系统设置壁纸"""
        try:
            # 尝试使用 gsettings (GNOME)
            import subprocess
            uri = f"file://{os.path.abspath(image_path)}"
            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri],
                check=True,
                capture_output=True,
            )
        except Exception:
            pass

    def set_random_wallpaper(self):
        """随机切换壁纸"""
        images = self.get_images()
        if not images:
            print("  [提示] 没有可用的壁纸图片")
            return False

        chosen = random.choice(images)
        print(f"  [切换] {os.path.basename(chosen)}")
        return self.set_wallpaper(chosen)

    def auto_rotate(self, interval=300, callback=None):
        """
        自动轮换壁纸

        Args:
            interval: 切换间隔（秒）
            callback: 回调函数，切换后调用
        """
        self._stop_flag = False
        used = set()
        images = self.get_images()

        if not images:
            print("  [提示] 没有可用的壁纸图片")
            return

        print(f"  [启动] 壁纸自动轮换，间隔 {interval} 秒")
        print(f"  [提示] 按 Ctrl+C 停止")

        try:
            while not self._stop_flag:
                available = [img for img in images if img not in used]
                if not available:
                    used.clear()
                    available = images

                chosen = random.choice(available)
                used.add(chosen)

                print(f"\r  [{time.strftime('%H:%M:%S')}] 切换壁纸: {os.path.basename(chosen)}", end="")

                self.set_wallpaper(chosen)

                if callback:
                    try:
                        callback(chosen)
                    except Exception:
                        pass

                for _ in range(interval):
                    if self._stop_flag:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\n  [停止] 壁纸轮换已停止")

    def stop_rotation(self):
        """停止壁纸轮换"""
        self._stop_flag = True

    def start_rotation_thread(self, interval=300):
        """在后台线程中启动壁纸轮换"""
        self._thread = threading.Thread(
            target=self.auto_rotate,
            args=(interval,),
            daemon=True,
        )
        self._thread.start()
        return self._thread

    def get_wallpaper_info(self):
        """获取当前壁纸信息"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
            )
            wallpaper, _ = winreg.QueryValueEx(key, "WallPaper")
            winreg.CloseKey(key)

            if wallpaper and os.path.exists(wallpaper):
                size = os.path.getsize(wallpaper)
                return {
                    "path": wallpaper,
                    "name": os.path.basename(wallpaper),
                    "size": size,
                    "size_str": self._format_size(size),
                }
            return {"path": wallpaper, "name": os.path.basename(wallpaper) if wallpaper else "None"}
        except Exception:
            return None

    @staticmethod
    def _format_size(size):
        """格式化文件大小"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def download_wallpaper(self, query, count=1):
        """
        从 Bing 下载壁纸

        Args:
            query: 搜索关键词 (保留功能)
            count: 下载数量
        """
        # 使用 Bing 每日壁纸 API
        try:
            import urllib.request
            import json

            print(f"  [下载] 正在获取 Bing 每日壁纸...")

            url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n={count}&mkt=zh-CN"
            url = url.format(count=count)

            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            downloaded = 0
            for item in data.get("images", []):
                img_url = "https://www.bing.com" + item.get("url", "")
                if not img_url:
                    continue

                name = item.get("copyright", "wallpaper").split("(")[0].strip()[:30]
                name = "".join(c for c in name if c not in '\\/:*?"<>|')
                if not name:
                    name = f"bing_wallpaper_{downloaded + 1}"

                save_path = self.folder / f"{name}.jpg"

                print(f"  [下载] {name}")
                urllib.request.urlretrieve(img_url, str(save_path))
                downloaded += 1

            print(f"  [完成] 下载了 {downloaded} 张壁纸到 {self.folder}")
            return downloaded

        except Exception as e:
            print(f"  [错误] 下载壁纸失败: {e}")
            return 0
