import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配_多模板
from 工具.读取配置 import 计算偏移位置, 读取配置
from 工具.日志打印 import 日志打印, 启动日志线程

mouse = Controller()

模板_花朵目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "03-收获", "模板")
模板_收花按钮 = os.path.join(
    os.path.dirname(__file__), "..", "素材", "03-收获", "按钮", "收获按钮.png"
)

cfg = 读取配置()
拖动间隔 = cfg["拖动间隔"]

def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

threading.Thread(target=_启动停止监听, daemon=True).start()

def 收获():
    启动日志线程()
    日志打印("=== 收获 ===")

    花朵列表 = 查找所有匹配_多模板(屏幕截图(), 模板_花朵目录, 阈值=0.75)

    if not 花朵列表:
        日志打印("未在屏幕上找到成熟的花朵")
        return

    日志打印(f"识别到 {len(花朵列表)} 朵花")
    for i, pos in enumerate(花朵列表):
        日志打印(f"  第 {i + 1} 朵: {pos}")

    日志打印("开始执行...（按 Esc 或 Ctrl+C 停止）")

    try:
        first = 花朵列表[0]
        first = 计算偏移位置(*first)
        mouse.position = first
        mouse.click(Button.left, 1)
        日志打印(f"已点击第一朵花 {first}，等待弹窗...")
        time.sleep(0.8)

        日志打印("正在查找收获按钮...")
        按钮位置 = 查找单个匹配(屏幕截图(), 模板_收花按钮, 阈值=0.7)
        if not 按钮位置:
            日志打印("未找到收获按钮")
            return
        按钮位置 = 计算偏移位置(*按钮位置)
        日志打印(f"收获按钮位置: {按钮位置}")

        bx, by = 按钮位置
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        日志打印(f"已按住收获按钮，开始拖动...")
        time.sleep(0.1)

        for i, (tx, ty) in enumerate(花朵列表):
            偏移位置 = 计算偏移位置(tx, ty)
            mouse.position = 偏移位置
            日志打印(f"经过第 {i + 1} 朵花: {偏移位置}")
            time.sleep(拖动间隔)

        mouse.release(Button.left)
        日志打印(f"=== 收获完成！共收获 {len(花朵列表)} 朵花 ===")

    except KeyboardInterrupt:
        日志打印("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    收获()