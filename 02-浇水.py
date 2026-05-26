import os
import sys
import threading
import time

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配_多模板
from 工具.读取配置 import 计算偏移位置, 读取配置

mouse = Controller()

模板_浇水目录 = os.path.join(os.path.dirname(__file__), "素材", "02-浇水")
模板_需要浇水 = os.path.join(os.path.dirname(__file__), "素材", "02-浇水", "模板")

cfg = 读取配置()
拖动间隔 = cfg["拖动间隔"]
最大上限 = cfg["最大上限"]


def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 浇水():
    print("=== 浇水 ===")

    需要浇水列表 = 查找所有匹配_多模板(屏幕截图(), 模板_需要浇水, 阈值=0.75)

    if not 需要浇水列表:
        print("未找到需要浇水的花")
        return

    if 最大上限 > 0:
        需要浇水列表 = 需要浇水列表[:最大上限]

    print(f"识别到 {len(需要浇水列表)} 朵需要浇水的花")
    for i, pos in enumerate(需要浇水列表):
        print(f"  第 {i + 1} 朵: {pos}")

    print("2 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(2)

    try:
        first = 需要浇水列表[0]
        first = 计算偏移位置(*first)
        mouse.position = first
        mouse.click(Button.left, 1)
        print(f"已点击第一朵花 {first}，等待弹窗...")
        time.sleep(0.8)

        print("正在查找浇水按钮...")
        浇水按钮 = 查找单个匹配(
            屏幕截图(), os.path.join(模板_浇水目录, "浇水按钮.png"), 阈值=0.7
        )
        if not 浇水按钮:
            print("未找到浇水按钮")
            return
        浇水按钮 = 计算偏移位置(*浇水按钮)
        print(f"浇水按钮位置: {浇水按钮}")

        bx, by = 浇水按钮
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"已按住浇水按钮，开始拖动...")
        time.sleep(0.1)

        for i, (tx, ty) in enumerate(需要浇水列表):
            偏移位置 = 计算偏移位置(tx, ty)
            mouse.position = 偏移位置
            print(f"经过第 {i + 1} 朵花: {偏移位置}")
            time.sleep(拖动间隔)

        mouse.release(Button.left)
        print(f"=== 浇水完成！共浇 {len(需要浇水列表)} 朵花 ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    浇水()
