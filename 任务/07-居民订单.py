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

模板目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "07-居民订单")

cfg = 读取配置()
最多提交次数 = cfg["居民订单提交尝试次数"]


def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 检查界面():
    路径 = os.path.join(模板目录, "02居民订单界面.png")
    if not os.path.exists(路径):
        return False
    return 查找单个匹配(屏幕截图(), 路径, 阈值=0.7) is not None


def 查找提交按钮():
    路径 = os.path.join(模板目录, "03-提交按钮.png")
    if not os.path.exists(路径):
        return None
    return 查找单个匹配(屏幕截图(), 路径, 阈值=0.7)


def 居民订单():
    启动日志线程()
    日志打印("=== 居民订单 ===")

    牌子路径 = os.path.join(模板目录, "居民订单的牌子.png")
    if os.path.exists(牌子路径):
        日志打印("正在查找居民订单牌子...")
        牌子位置 = 查找单个匹配(屏幕截图(), 牌子路径, 阈值=0.7)
        if 牌子位置:
            mouse.position = 牌子位置
            mouse.click(Button.left, 1)
            日志打印(f"✅ 已点击居民订单牌子 {牌子位置}")
            time.sleep(0.5)

    if not 检查界面():
        日志打印("当前不在居民订单界面，退出")
        return

    提交数 = 0
    for 次 in range(1, 最多提交次数 + 1):
        位置 = 查找提交按钮()
        if not 位置:
            break

        mouse.position = 位置
        mouse.click(Button.left, 1)
        提交数 += 1
        日志打印(f"✅ 已提交第 {提交数} 个订单 {位置}")
        time.sleep(0.3)

    日志打印(f"=== 居民订单完成！共提交 {提交数} 个订单 ===")

    # 关闭界面
    关闭路径 = os.path.join(模板目录, "居民订单-关闭.png")
    if os.path.exists(关闭路径):
        日志打印("正在关闭居民订单界面...")
        关闭位置 = 查找单个匹配(屏幕截图(), 关闭路径, 阈值=0.7)
        if 关闭位置:
            mouse.position = 关闭位置
            mouse.click(Button.left, 1)
            日志打印(f"✅ 已关闭 {关闭位置}")


if __name__ == "__main__":
    居民订单()