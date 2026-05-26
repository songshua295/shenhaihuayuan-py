"""MSS 截图 + OpenCV 模板匹配 工具模块"""

import os

import cv2
import mss
import numpy as np


def 屏幕截图():
    """用 MSS 截取全屏，返回 OpenCV 格式 (numpy BGR)"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 主显示器
        img = sct.grab(monitor)
        return cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)


def 查找所有匹配(截图, 模板路径, 阈值=0.75):
    """在截图中查找所有匹配模板的位置，返回按行排序的 [(x,y),...] 列表"""
    if not os.path.exists(模板路径):
        print(f"错误：找不到模板图片 {模板路径}")
        return []

    模板 = cv2.imdecode(np.fromfile(模板路径, dtype=np.uint8), cv2.IMREAD_COLOR)
    if 模板 is None:
        print(f"错误：无法读取模板图片 {模板路径}")
        return []

    模板_h, 模板_w = 模板.shape[:2]
    结果 = cv2.matchTemplate(截图, 模板, cv2.TM_CCOEFF_NORMED)

    pos_list = []
    for pt in zip(*np.where(结果 >= 阈值)[::-1]):
        中心 = (pt[0] + 模板_w // 2, pt[1] + 模板_h // 2)
        pos_list.append(中心)

    return _去重合并(pos_list, 模板_w, 模板_h)


def 查找所有匹配_多模板(截图, 模板文件夹, 阈值=0.75):
    """用文件夹内所有 PNG 模板分别匹配，合并结果"""
    if not os.path.exists(模板文件夹):
        print(f"错误：找不到模板文件夹 {模板文件夹}")
        return []

    png列表 = [f for f in os.listdir(模板文件夹) if f.endswith(".png")]
    if not png列表:
        print(f"错误：模板文件夹内没有 PNG 图片")
        return []

    全部结果 = []
    for 文件名 in png列表:
        路径 = os.path.join(模板文件夹, 文件名)
        模板 = cv2.imdecode(np.fromfile(路径, dtype=np.uint8), cv2.IMREAD_COLOR)
        if 模板 is None:
            continue

        模板_h, 模板_w = 模板.shape[:2]
        结果 = cv2.matchTemplate(截图, 模板, cv2.TM_CCOEFF_NORMED)

        for pt in zip(*np.where(结果 >= 阈值)[::-1]):
            中心 = (pt[0] + 模板_w // 2, pt[1] + 模板_h // 2)
            全部结果.append(中心)

    if not 全部结果:
        return []

    return _去重合并(全部结果, 60, 60)  # 按最大可能的模板尺寸去重


def 查找单个匹配(截图, 模板路径, 阈值=0.7):
    """在截图中查找最佳匹配，返回 (x,y) 或 None"""
    if not os.path.exists(模板路径):
        print(f"错误：找不到模板图片 {模板路径}")
        return None

    模板 = cv2.imdecode(np.fromfile(模板路径, dtype=np.uint8), cv2.IMREAD_COLOR)
    if 模板 is None:
        return None

    模板_h, 模板_w = 模板.shape[:2]
    结果 = cv2.matchTemplate(截图, 模板, cv2.TM_CCOEFF_NORMED)
    _, 最大值, _, 最大位置 = cv2.minMaxLoc(结果)

    if 最大值 >= 阈值:
        中心 = (最大位置[0] + 模板_w // 2, 最大位置[1] + 模板_h // 2)
        return 中心
    return None


def _去重合并(坐标列表, 模板宽, 模板高):
    """合并距离过近的坐标，按 Y→X 排序"""
    if not 坐标列表:
        return []

    坐标列表.sort(key=lambda p: (p[1], p[0]))
    结果 = []
    for p in 坐标列表:
        if (
            not 结果
            or abs(p[0] - 结果[-1][0]) > 模板宽 // 2
            or abs(p[1] - 结果[-1][1]) > 模板高 // 2
        ):
            结果.append(p)
    return 结果
