import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配_多模板
from 工具.读取配置 import 读取配置

mouse = Controller()

模板目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "08-偷花")
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


def 偷花():
    print("=== 偷花 ===")

    偷花按钮目录 = os.path.join(模板目录, "偷花按钮")
    次数模板 = os.path.join(模板目录, "摘取次数.png")

    if not os.path.exists(偷花按钮目录):
        print("模板目录 偷花按钮/ 不存在")
        return

    # 先识别摘取次数位置，确定筛选范围
    次数上限_y = None
    if os.path.exists(次数模板):
        次数位置 = 查找单个匹配(屏幕截图(), 次数模板, 阈值=0.8)
        if 次数位置:
            次数上限_y = 次数位置[1]
            print(f"摘取次数位置: {次数位置}")

    # 用偷花按钮目录下所有模板匹配
    截图 = 屏幕截图()
    所有匹配 = 查找所有匹配_多模板(截图, 偷花按钮目录, 阈值=0.8)

    if 次数上限_y is not None:
        候选 = [p for p in 所有匹配 if p[1] <= 次数上限_y]
    else:
        候选 = 所有匹配

    if not 候选:
        print("未找到偷花按钮")
        return

    print(f"找到 {len(候选)} 个偷花按钮，按顺序点击")

    for 次, 位置 in enumerate(候选, 1):
        mouse.position = 位置
        mouse.click(Button.left, 1)
        print(f"第 {次}/{len(候选)} 次：已点击偷花按钮 {位置}")
        time.sleep(拖动间隔)

    print(f"=== 偷花完成！共摘取 {len(候选)} 次 ===")


if __name__ == "__main__":
    偷花()
