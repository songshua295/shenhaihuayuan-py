import os
import sys
import threading
import time

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配_多模板

mouse = Controller()

模板_浇水目录 = os.path.join(os.path.dirname(__file__), "assets", "浇水")
模板_需要浇水 = os.path.join(
    os.path.dirname(__file__), "assets", "浇水", "需要浇水模板"
)


# 后台 Esc 监听
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

    # ========== 第1步：找需要浇水的花并点击，让按钮弹出来 ==========
    print("正在查找需要浇水的花...")
    需要浇水列表 = 查找所有匹配_多模板(屏幕截图(), 模板_需要浇水, 阈值=0.75)

    if not 需要浇水列表:
        print("未找到需要浇水的花")
        return

    first = 需要浇水列表[0]
    mouse.position = first
    mouse.click(Button.left, 1)
    print(f"已点击需要浇水的花 {first}，等待弹窗...")
    time.sleep(0.8)

    # ========== 第2步：截图找浇水按钮 ==========
    print("正在查找浇水按钮...")
    浇水按钮 = 查找单个匹配(
        屏幕截图(), os.path.join(模板_浇水目录, "浇水按钮.png"), 阈值=0.7
    )
    if not 浇水按钮:
        print("未找到浇水按钮，请确认模板 assets/浇水/浇水按钮.png 是否正确")
        return
    print(f"浇水按钮位置: {浇水按钮}")

    print("2 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(2)

    try:
        # ========== 第3步：移到浇水按钮，按住 ==========
        bx, by = 浇水按钮
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"已按住浇水按钮，开始扫描需要浇水的花并拖动...")
        time.sleep(0.2)

        # ========== 第4步：边按住边实时扫描，逐个拖动 ==========
        已浇数 = 0
        while True:
            当前截图 = 屏幕截图()
            当前需要浇水 = 查找所有匹配_多模板(当前截图, 模板_需要浇水, 阈值=0.75)

            if not 当前需要浇水:
                print("所有需要浇水的花已浇完！")
                break

            鼠标位置 = mouse.position
            最近花 = min(
                当前需要浇水,
                key=lambda p: (p[0] - 鼠标位置[0]) ** 2 + (p[1] - 鼠标位置[1]) ** 2,
            )

            mouse.position = 最近花
            已浇数 += 1
            print(f"已浇 {已浇数}: 拖动到 ({最近花[0]}, {最近花[1]})")
            time.sleep(0.3)

        # ========== 第5步：松开 ==========
        mouse.release(Button.left)
        print(f"=== 浇水完成！共浇 {已浇数} 朵花 ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    浇水()
