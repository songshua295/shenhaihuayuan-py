import os
import sys
import threading
import time

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配_多模板

mouse = Controller()

模板_加速目录 = os.path.join(os.path.dirname(__file__), "assets", "加速")
模板_需加速花 = os.path.join(os.path.dirname(__file__), "assets", "加速", "模板")


# 后台 Esc 监听
def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 加速():
    print("=== 加速 ===")

    # ========== 第1次识别：找需要加速的花 ==========
    print("正在识别需要加速的花...")
    需加速列表 = 查找所有匹配_多模板(屏幕截图(), 模板_需加速花, 阈值=0.75)

    if not 需加速列表:
        print("未找到需要加速的花")
        return

    print(f"识别到 {len(需加速列表)} 朵需要加速的花")
    for i, pos in enumerate(需加速列表):
        print(f"  第 {i + 1} 朵: {pos}")

    print("2 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(2)

    try:
        # ========== 点击第一朵花，触发弹窗 ==========
        first = 需加速列表[0]
        mouse.position = first
        mouse.click(Button.left, 1)
        print(f"已点击第一朵花 {first}，等待弹窗...")
        time.sleep(0.8)

        # ========== 检查是否有免费加速按钮 ==========
        免费加速路径 = os.path.join(模板_加速目录, "免费加速按钮.png")
        if os.path.exists(免费加速路径):
            print("正在查找免费加速按钮...")
            免费按钮位置 = 查找单个匹配(屏幕截图(), 免费加速路径, 阈值=0.7)
            if 免费按钮位置:
                mouse.position = 免费按钮位置
                mouse.click(Button.left, 1)
                print(f"已点击免费加速按钮 {免费按钮位置}，等待生效...")
                time.sleep(0.5)

                # 重新扫描，如果没花需要加速了就退出
                print("免费加速后重新扫描需要加速的花...")
                需加速列表 = 查找所有匹配_多模板(屏幕截图(), 模板_需加速花, 阈值=0.75)
                if not 需加速列表:
                    print("免费加速后所有花已加速完！")
                    return
                print(f"还有 {len(需加速列表)} 朵需要加速，继续执行拖动")
            else:
                print("未找到免费加速按钮，跳过")

        # ========== 重新截图，找加速按钮 ==========
        print("正在查找加速按钮...")
        按钮位置 = 查找单个匹配(
            屏幕截图(), os.path.join(模板_加速目录, "加速按钮.png"), 阈值=0.7
        )

        if not 按钮位置:
            print("未找到加速按钮")
            return

        print(f"加速按钮位置: {按钮位置}")

        # ========== 移到按钮位置，按住 ==========
        bx, by = 按钮位置
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"已按住加速按钮，开始拖动（实时识别位置，不怕偏移）...")
        time.sleep(0.2)

        # ========== 实时扫描拖动 ==========
        已加速数 = 0
        while True:
            当前截图 = 屏幕截图()
            当前需加速 = 查找所有匹配_多模板(当前截图, 模板_需加速花, 阈值=0.75)

            if not 当前需加速:
                print("所有花已加速完！")
                break

            鼠标位置 = mouse.position
            最近花 = min(
                当前需加速,
                key=lambda p: (p[0] - 鼠标位置[0]) ** 2 + (p[1] - 鼠标位置[1]) ** 2,
            )

            mouse.position = 最近花
            已加速数 += 1
            print(f"已加速 {已加速数}: 拖动到 ({最近花[0]}, {最近花[1]})")
            time.sleep(0.3)

        # ========== 松开 ==========
        mouse.release(Button.left)
        print(f"=== 加速完成！共加速 {已加速数} 朵花 ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    加速()
