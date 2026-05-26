import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配_多模板
from 工具.读取配置 import 计算偏移位置, 读取配置

mouse = Controller()

模板_花朵目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "04-加速", "模板")
模板_铲除目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "05-铲除")

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


def 铲除():
    print("=== 铲除 ===")

    需铲除列表 = 查找所有匹配_多模板(屏幕截图(), 模板_花朵目录, 阈值=0.75)

    if not 需铲除列表:
        print("未找到需要铲除的花")
        return

    if 最大上限 > 0:
        需铲除列表 = 需铲除列表[:最大上限]

    print(f"识别到 {len(需铲除列表)} 朵需要铲除的花")
    for i, pos in enumerate(需铲除列表):
        print(f"  第 {i + 1} 朵: {pos}")

    print("2 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(2)

    try:
        first = 需铲除列表[0]
        first = 计算偏移位置(*first)
        mouse.position = first
        mouse.click(Button.left, 1)
        print(f"已点击第一朵花 {first}，等待弹窗...")
        time.sleep(0.8)

        print("正在查找铲除按钮...")
        按钮位置 = 查找单个匹配(
            屏幕截图(), os.path.join(模板_铲除目录, "按钮", "铲除按钮.png"), 阈值=0.7
        )
        if not 按钮位置:
            print("未找到铲除按钮")
            return
        按钮位置 = 计算偏移位置(*按钮位置)
        print(f"铲除按钮位置: {按钮位置}")

        bx, by = 按钮位置
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"已按住铲除按钮，开始实时扫描拖动...")
        time.sleep(0.2)

        已铲除数 = 0
        while True:
            if 最大上限 > 0 and 已铲除数 >= 最大上限:
                print(f"已达到上限 {最大上限}，停止")
                break

            当前截图 = 屏幕截图()
            当前需铲除 = 查找所有匹配_多模板(当前截图, 模板_花朵目录, 阈值=0.75)

            if not 当前需铲除:
                print("所有花已铲除完！")
                break

            鼠标位置 = mouse.position
            最近花 = min(
                当前需铲除,
                key=lambda p: (p[0] - 鼠标位置[0]) ** 2 + (p[1] - 鼠标位置[1]) ** 2,
            )
            最近花 = 计算偏移位置(*最近花)

            mouse.position = 最近花
            已铲除数 += 1
            print(f"已铲除 {已铲除数}: 拖动到 ({最近花[0]}, {最近花[1]})")
            time.sleep(拖动间隔)

        mouse.release(Button.left)
        print(f"=== 铲除完成！共铲除 {已铲除数} 朵花 ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    铲除()
