"""读取配置/设置.txt 全局配置"""

import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "配置", "设置.txt")

# 默认值
_配置缓存 = None


def 读取配置():
    global _配置缓存
    if _配置缓存 is not None:
        return _配置缓存

    配置 = {
        "拖动间隔": 0.2,
        "点击偏移": "中心",
        "偏移像素": 15,
        "最大上限": 0,
    }

    if not os.path.exists(_CONFIG_PATH):
        return 配置

    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key in ("拖动间隔", "偏移像素", "最大上限"):
                try:
                    配置[key] = int(value) if key == "最大上限" else float(value)
                except ValueError:
                    pass
            elif key == "点击偏移":
                if value in ("中心", "左上角", "右下角", "下端"):
                    配置[key] = value

    _配置缓存 = 配置
    return 配置


def 计算偏移位置(x, y):
    """根据配置的点击偏移和偏移像素，返回调整后的坐标"""
    配置 = 读取配置()
    偏移模式 = 配置["点击偏移"]
    像素 = 配置["偏移像素"]

    if 偏移模式 == "中心":
        return (x, y)
    elif 偏移模式 == "左上角":
        return (x - 像素, y - 像素)
    elif 偏移模式 == "右下角":
        return (x + 像素, y + 像素)
    elif 偏移模式 == "下端":
        return (x, y + 像素)
    return (x, y)
