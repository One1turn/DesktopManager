# Windows 桌面美化整理工具

> 一个功能完善的 Windows 桌面管理工具，包含文件整理、壁纸管理、系统监控和快捷方式管理。

## 功能概览

| 功能 | 说明 |
|------|------|
| 📁 桌面文件整理 | 按文件类型自动分类到对应文件夹 |
| 🖼️ 壁纸管理 | 随机切换、定时轮换、Bing 壁纸下载 |
| 📊 系统监控 | CPU/内存/磁盘使用率实时监控 |
| 🔗 快捷方式管理 | 查找、验证、清理无效快捷方式 |
| ✨ 一键美化 | 整理 + 换壁纸 + 清理 一步到位 |

## 快速开始

### 1. 安装依赖

```bash
cd DesktopManager
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

### 3. 使用菜单

启动后会显示交互式菜单，输入数字选择功能即可。

## 项目结构

```
DesktopManager/
├── main.py                    # 主程序入口
├── config.json                # 配置文件 (首次运行自动生成)
├── requirements.txt           # Python 依赖
├── README.md                  # 说明文档
└── modules/
    ├── desktop_organizer.py   # 桌面文件整理模块
    ├── wallpaper_manager.py   # 壁纸管理模块
    ├── system_monitor.py      # 系统监控模块
    └── shortcut_manager.py    # 快捷方式管理模块
```

## 配置说明

首次运行会自动生成 `config.json` 配置文件：

```json
{
  "desktop_path": "C:\\Users\\你的用户名\\Desktop",
  "wallpaper_folder": "C:\\Users\\你的用户名\\Pictures\\Wallpapers",
  "wallpaper_interval": 300,
  "organize_rules": {
    "Images": [".jpg", ".jpeg", ".png", ...],
    "Documents": [".pdf", ".doc", ".txt", ...],
    "Videos": [".mp4", ".avi", ".mkv", ...],
    "Music": [".mp3", ".wav", ".flac", ...],
    "Archives": [".zip", ".rar", ".7z", ...],
    "Programs": [".exe", ".msi", ".bat", ...],
    "Code": [".py", ".js", ".java", ...]
  },
  "monitor_interval": 5,
  "auto_organize": false,
  "auto_wallpaper": false
}
```

## 分类规则

| 文件夹 | 扩展名 |
|--------|--------|
| Images | .jpg .jpeg .png .gif .bmp .webp .svg .ico |
| Documents | .pdf .doc .docx .txt .xls .xlsx .ppt .pptx .csv .md |
| Videos | .mp4 .avi .mkv .mov .wmv .flv |
| Music | .mp3 .wav .flac .aac .ogg .wma |
| Archives | .zip .rar .7z .tar .gz .bz2 |
| Programs | .exe .msi .bat .cmd .ps1 |
| Code | .py .js .java .cpp .c .h .html .css .json .xml |
| Others | 以上未匹配的文件 |

## 功能详解

### 桌面文件整理

- 自动扫描桌面所有文件
- 按扩展名分类移动到对应文件夹
- 文件名冲突自动重命名 (xxx_1.txt)
- 支持撤销整理（恢复文件到桌面）
- 支持查找重复文件

### 壁纸管理

- 随机切换壁纸
- 按序号选择壁纸
- 定时自动轮换（可自定义间隔）
- 下载 Bing 每日壁纸
- 支持格式: .jpg .jpeg .png .bmp .webp

### 系统监控

- CPU 使用率和核心数
- 内存使用率/总量/已用
- 磁盘使用率/总量/已用
- 网络流量统计
- 系统运行时间
- CPU 温度（如可用）
- 支持 psutil 和降级模式（无需额外依赖）

### 快捷方式管理

- 自动解析 .lnk 文件目标路径
- 验证快捷方式是否有效
- 一键清理无效快捷方式
- 创建新快捷方式
- 导出快捷方式列表

## 技术特点

- **零配置启动**: 首次运行自动生成配置文件
- **降级兼容**: psutil 不可用时自动降级到 ctypes
- **不依赖 pywin32**: 快捷方式解析有内置实现和 PowerShell 回退
- **线程安全**: 壁纸轮换支持后台线程
- **文件冲突处理**: 自动重命名避免覆盖

## 系统要求

- Windows 7/8/10/11
- Python 3.8+
- 推荐安装 psutil (pip install psutil)

## 许可证

MIT License

---

作者: Operit AI  
创建日期: 2026-08-14
