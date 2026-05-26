import os
import sys
import threading
import time

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配_多模板

mouse = Controller()

模板_花朵目录 = os.path.join(os.path.dirname(__file__), "assets", "花朵模板")
模板_收花按钮 = os.path.join(os.path.dirname(__file__), "assets", "收获按钮.png")


# 后台 Esc 监听
def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 收获():
    print("=== 收获 ===")

    # ========== 第1次识别：找所有成熟的花 ==========
    print("正在识别花朵位置...")
    花朵列表 = 查找所有匹配_多模板(屏幕截图(), 模板_花朵目录, 阈值=0.75)

    if not 花朵列表:
        print("未在屏幕上找到成熟的花朵")
        return

    print(f"识别到 {len(花朵列表)} 朵花")
    for i, pos in enumerate(花朵列表):
        print(f"  第 {i + 1} 朵: {pos}")

    print("2 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(2)

    try:
        # ========== 点击第一朵花，触发弹窗 ==========
        first = 花朵列表[0]
        mouse.position = first
        mouse.click(Button.left, 1)
        print(f"已点击第一朵花 {first}，等待弹窗...")
        time.sleep(0.8)

        # ========== 第2次识别：找收获按钮 ==========
        print("正在查找收获按钮...")
        按钮位置 = 查找单个匹配(屏幕截图(), 模板_收花按钮, 阈值=0.7)

        if not 按钮位置:
            print("未找到收获按钮")
            return

        print(f"收获按钮位置: {按钮位置}")

        # ========== 移到按钮位置，按住 ==========
        bx, by = 按钮位置
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"已按住收获按钮，开始拖动...")
        time.sleep(0.1)

        # ========== 拖动经过所有花 ==========
        for i, (tx, ty) in enumerate(花朵列表):
            mouse.position = (tx, ty)
            print(f"经过第 {i + 1} 朵花: ({tx}, {ty})")
            time.sleep(0.2)

        # ========== 松开 ==========
        mouse.release(Button.left)
        print(f"=== 收获完成！共收获 {len(花朵列表)} 朵花 ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    收获()
