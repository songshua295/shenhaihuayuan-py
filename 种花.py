import os
import sys
import threading
import time

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配

mouse = Controller()

模板_花种目录 = os.path.join(os.path.dirname(__file__), "assets", "花种模板")
模板_空地 = os.path.join(os.path.dirname(__file__), "assets", "花种模板", "0空地.png")


# 后台 Esc 监听
def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 列出花种():
    种子列表 = []
    for f in sorted(os.listdir(模板_花种目录)):
        if f.endswith(".png") and f != "0空地.png":
            种子列表.append(f.replace(".png", ""))
    return 种子列表


def 选择花种():
    种子列表 = 列出花种()
    if not 种子列表:
        print("错误：花种模板目录为空，请放入花种图片")
        return None

    print("\n可选花种：")
    for i, name in enumerate(种子列表):
        print(f"  [{i + 1}] {name}")

    while True:
        try:
            choice = input(f"\n请选择要种的花（1~{len(种子列表)}）：").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(种子列表):
                选中 = 种子列表[idx]
                路径 = os.path.join(模板_花种目录, f"{选中}.png")
                print(f"已选择：{选中}")
                return 路径, 选中
            else:
                print(f"请输入 1~{len(种子列表)} 之间的数字")
        except ValueError:
            print("请输入有效数字")


def 种花():
    print("=== 种花 ===")

    # ========== 第1步：选择花种 ==========
    花种结果 = 选择花种()
    if not 花种结果:
        return
    花种模板路径, 花种名称 = 花种结果

    # ========== 第2步：截图找花种位置 ==========
    print(f"\n正在识别花种位置...")
    截图 = 屏幕截图()
    花种位置 = 查找单个匹配(截图, 花种模板路径, 阈值=0.7)
    if not 花种位置:
        print(f"未在屏幕上找到【{花种名称}】，请确认该花种可见")
        return
    print(f"【{花种名称}】位置: {花种位置}")

    print(f"\n2 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(2)

    try:
        # ========== 第3步：移到花种位置，按住（不松开） ==========
        sx, sy = 花种位置
        mouse.position = (sx, sy)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"已按住【{花种名称}】，开始扫描空地并拖动...")
        time.sleep(0.2)

        # ========== 第4步：边拖动边实时扫描空地 ==========
        已种植数 = 0
        while True:
            # 实时截图找当前剩余空地
            当前截图 = 屏幕截图()
            当前空地 = 查找所有匹配(当前截图, 模板_空地, 阈值=0.75)

            if not 当前空地:
                print("所有空地已种完！")
                break

            # 找到离当前鼠标最近的空地，减少无效移动
            鼠标位置 = mouse.position
            最近空地 = min(
                当前空地,
                key=lambda p: (p[0] - 鼠标位置[0]) ** 2 + (p[1] - 鼠标位置[1]) ** 2,
            )

            # 拖动到该空地
            mouse.position = 最近空地
            已种植数 += 1
            print(f"已种 {已种植数}: 拖动到空地 ({最近空地[0]}, {最近空地[1]})")
            time.sleep(0.3)  # 给游戏反应时间，同时等待种植生效

        # ========== 第5步：松开 ==========
        mouse.release(Button.left)
        print(f"=== 【{花种名称}】种植完成！共种植 {已种植数} 块空地 ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    种花()
