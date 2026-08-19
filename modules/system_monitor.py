#!/usr/bin/env python3
"""
系统状态监控模块
功能：监控CPU、内存、磁盘使用率和系统运行时间
"""

import os
import time
import platform
from datetime import datetime, timedelta


class SystemMonitor:
    """系统状态监控器"""

    def __init__(self):
        self._boot_time = None

    def get_system_info(self):
        """获取系统信息"""
        info = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "os": platform.system(),
            "os_version": platform.version(),
            "hostname": platform.node(),
        }

        try:
            import psutil
            self._get_info_with_psutil(info)
        except ImportError:
            self._get_info_without_psutil(info)

        return info

    def _get_info_with_psutil(self, info):
        """使用 psutil 获取系统信息"""
        import psutil

        # CPU
        info["cpu_percent"] = psutil.cpu_percent(interval=0.5)
        info["cpu_count"] = psutil.cpu_count()
        info["cpu_freq"] = psutil.cpu_freq()

        # 内存
        mem = psutil.virtual_memory()
        info["memory_total"] = mem.total / (1024 ** 3)
        info["memory_used"] = mem.used / (1024 ** 3)
        info["memory_percent"] = mem.percent

        # 磁盘
        disk = psutil.disk_usage("/")
        info["disk_total"] = disk.total / (1024 ** 3)
        info["disk_used"] = disk.used / (1024 ** 3)
        info["disk_free"] = disk.free / (1024 ** 3)
        info["disk_percent"] = disk.percent

        # 网络
        net = psutil.net_io_counters()
        info["net_sent"] = net.bytes_sent / (1024 ** 2)
        info["net_recv"] = net.bytes_recv / (1024 ** 2)

        # 开机时长
        if self._boot_time is None:
            self._boot_time = psutil.boot_time()
        uptime_seconds = time.time() - self._boot_time
        info["uptime"] = self._format_uptime(uptime_seconds)

        # CPU 温度 (如果可用)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        info["cpu_temp"] = entries[0].current
                        break
        except (AttributeError, Exception):
            pass

    def _get_info_without_psutil(self, info):
        """不使用 psutil 获取系统信息 (降级方案)"""
        import ctypes

        # CPU 使用率 (Windows)
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        mem_status = MEMORYSTATUSEX()
        mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))

        info["cpu_percent"] = 0.0
        info["cpu_count"] = os.cpu_count()
        info["memory_total"] = mem_status.ullTotalPhys / (1024 ** 3)
        info["memory_used"] = (mem_status.ullTotalPhys - mem_status.ullAvailPhys) / (1024 ** 3)
        info["memory_percent"] = mem_status.dwMemoryLoad

        # 磁盘
        try:
            total, used, free = shutil.disk_usage("/")
            info["disk_total"] = total / (1024 ** 3)
            info["disk_used"] = used / (1024 ** 3)
            info["disk_free"] = free / (1024 ** 3)
            info["disk_percent"] = (used / total) * 100
        except Exception:
            info["disk_total"] = 0
            info["disk_used"] = 0
            info["disk_percent"] = 0

        # 开机时长 (Windows)
        try:
            GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
            GetTickCount64.restype = ctypes.c_ulonglong
            tick_count = GetTickCount64()
            info["uptime"] = self._format_uptime(tick_count / 1000)
        except Exception:
            info["uptime"] = "N/A"

    @staticmethod
    def _format_uptime(seconds):
        """格式化运行时间"""
        try:
            seconds = int(seconds)
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            parts = []
            if days > 0:
                parts.append(f"{days}天")
            parts.append(f"{hours}小时")
            parts.append(f"{minutes}分")
            parts.append(f"{seconds}秒")

            return " ".join(parts)
        except Exception:
            return "N/A"

    def get_top_processes(self, count=10):
        """获取占用 CPU 最高的进程"""
        try:
            import psutil

            processes = []
            for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    processes.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cpu": proc.info["cpu_percent"],
                        "memory": proc.info["memory_percent"],
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            processes.sort(key=lambda x: x["cpu"], reverse=True)
            return processes[:count]

        except ImportError:
            return []

    def get_network_info(self):
        """获取网络信息"""
        try:
            import psutil
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }
        except ImportError:
            return {}
