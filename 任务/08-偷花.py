import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配

mouse = Controller()

模板_摘取 = os.path.join(os.path.dirname(__file__), "..", "素材", "08-偷花", "摘取.png")


def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 偷花():
    print("=== 偷花 ===")

    if not os.path.exists(模板_摘取):
        print("模板 摘取.png 不存在")
        return

    for 次 in range(1, 1001):
        位置 = 查找单个匹配(屏幕截图(), 模板_摘取, 阈值=0.7)
        if not 位置:
            if 次 == 1:
                print("未找到摘取按钮")
            else:
                print(f"已摘完，共摘取 {次 - 1} 次")
            break

        mouse.position = 位置
        mouse.click(Button.left, 1)
        print(f"第 {次} 次：已点击摘取 {位置}")
        time.sleep(0.5)

    print("=== 偷花完成！ ===")


if __name__ == "__main__":
    偷花()
