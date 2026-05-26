import os
import sys
import threading
import time

# 添加项目根目录到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配

mouse = Controller()

模板目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "任务素材", "顾客订单")


def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 点击模板(文件名, 描述, 等待=1.0):
    路径 = os.path.join(模板目录, 文件名)
    if not os.path.exists(路径):
        return False

    print(f"正在查找【{描述}】...")
    位置 = 查找单个匹配(屏幕截图(), 路径, 阈值=0.7)
    if not 位置:
        print(f"  ❌ 未找到【{描述}】")
        return False

    mouse.position = 位置
    mouse.click(Button.left, 1)
    print(f"  ✅ 已点击【{描述}】{位置}")
    time.sleep(等待)
    return True


def 顾客订单():
    print("=== 顾客订单 ===")

    # ========== 分支1：先检查是否不可制作 ==========
    if 点击模板("不可制作花瓶的.png", "不可制作花瓶的", 等待=1.0):
        print("该订单缺货，处理中...")
        点击模板("暂时没货.png", "暂时没货", 等待=1.0)
        print("=== 缺货处理完成！ ===")
        return

    # ========== 分支2：可制作流程 ==========
    if not 点击模板("可制作花瓶的.png", "可制作花瓶的", 等待=1.5):
        print("没有可处理的订单")
        return

    点击模板("前往制作.png", "前往制作", 等待=1.5)
    点击模板("制作.png", "制作", 等待=2.0)
    点击模板("交付前的确定.png", "交付前的确定", 等待=1.0)
    点击模板("交付.png", "交付", 等待=1.0)

    print("=== 顾客订单完成！ ===")


if __name__ == "__main__":
    顾客订单()
