import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配
from 工具.读取配置 import 读取配置
from 工具.日志打印 import 日志打印, 启动日志线程

mouse = Controller()

模板目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "08-顾客订单")
居民订单模板目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "07-居民订单")
cfg = 读取配置()
拖动间隔 = cfg["拖动间隔"]
尝试次数 = 2
重试等待秒 = 1

def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

threading.Thread(target=_启动停止监听, daemon=True).start()

def 点击模板(文件名, 描述, 等待=1):
    路径 = os.path.join(模板目录, 文件名)
    if not os.path.exists(路径):
        return False

    日志打印(f"  正在查找【{描述}】...")
    位置 = 查找单个匹配(屏幕截图(), 路径, 阈值=0.7)
    if not 位置:
        return False

    mouse.position = 位置
    mouse.click(Button.left, 1)
    日志打印(f"  ✅ 已点击【{描述}】{位置}")
    time.sleep(等待)
    return True

def 交付流程():
    点击模板("交付前的确定.png", "交付前的确定")
    点击模板("交付.png", "交付")
    点击模板("点击任意空白处关闭.png", "任意空白处关闭")

def 处理组团取消提示():
    取消提示路径 = os.path.join(居民订单模板目录, "组团订单-取消提示.png")
    确定按钮路径 = os.path.join(居民订单模板目录, "组团订单-确定.png")
    if os.path.exists(取消提示路径) and os.path.exists(确定按钮路径):
        取消提示位置 = 查找单个匹配(屏幕截图(), 取消提示路径, 阈值=0.7)
        if 取消提示位置:
            日志打印("  检测到组团订单取消提示，点击确定")
            确定位置 = 查找单个匹配(屏幕截图(), 确定按钮路径, 阈值=0.7)
            if 确定位置:
                mouse.position = 确定位置
                mouse.click(Button.left, 1)
                time.sleep(0.5)

def 处理一个订单():
    for 尝试 in range(1, 尝试次数 + 1):
        if 点击模板("花瓶已制作好的.png", "花瓶已制作好的"):
            日志打印("  → 已制作好，直接交付")
            交付流程()
            处理组团取消提示()
            return True

        if 点击模板("不可制作花瓶的.png", "不可制作花瓶的"):
            日志打印("  → 缺货处理")
            点击模板("暂时没货.png", "暂时没货")
            处理组团取消提示()
            return True

        if 点击模板("可制作花瓶的.png", "可制作花瓶的"):
            日志打印("  → 需要制作")
            点击模板("前往制作.png", "前往制作")
            点击模板("制作.png", "制作", 等待=2.0)
            交付流程()
            处理组团取消提示()
            return True

        if 尝试 < 尝试次数:
            日志打印(f"  未识别到订单，等待 {重试等待秒} 秒后重试 ({尝试}/{尝试次数})")
            time.sleep(重试等待秒)

    日志打印("  多次重试仍未识别到订单，结束")
    return False

def 顾客订单():
    启动日志线程()
    日志打印("=== 顾客订单 ===")

    处理数 = 0
    for 次 in range(1, 4):
        日志打印(f"\n--- 第 {次}/3 次 ---")
        if 处理一个订单():
            处理数 += 1
        else:
            日志打印("没有更多订单，结束")
            break

    日志打印(f"\n=== 顾客订单完成！共处理 {处理数} 个订单 ===")


if __name__ == "__main__":
    顾客订单()