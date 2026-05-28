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

模板_加速目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "04-加速")
模板_需加速花 = os.path.join(os.path.dirname(__file__), "..", "素材", "04-加速", "模板")

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

def 加速():
    启动日志线程()
    日志打印("=== 加速 ===")

    # ========== 第1次识别：找所有需要加速的花 ==========
    需加速列表 = 查找所有匹配_多模板(屏幕截图(), 模板_需加速花, 阈值=0.75)

    if not 需加速列表:
        日志打印("未找到需要加速的花")
        return

    if 最大上限 > 0:
        需加速列表 = 需加速列表[:最大上限]

    日志打印(f"识别到 {len(需加速列表)} 朵需要加速的花")
    for i, pos in enumerate(需加速列表):
        日志打印(f"  第 {i + 1} 朵: {pos}")

    try:
        # ========== 点击第一朵花，触发弹窗 ==========
        first = 需加速列表[0]
        first = 计算偏移位置(*first)
        mouse.position = first
        mouse.click(Button.left, 1)
        日志打印(f"已点击第一朵花 {first}，等待弹窗...")
        time.sleep(0.8)

        # ========== 检查免费加速按钮 ==========
        免费加速路径 = os.path.join(模板_加速目录, "按钮", "免费加速按钮.png")
        if os.path.exists(免费加速路径):
            日志打印("正在查找免费加速按钮...")
            免费按钮位置 = 查找单个匹配(屏幕截图(), 免费加速路径, 阈值=0.7)
            if 免费按钮位置:
                免费按钮位置 = 计算偏移位置(*免费按钮位置)
                mouse.position = 免费按钮位置
                mouse.click(Button.left, 1)
                日志打印(f"已点击免费加速按钮 {免费按钮位置}，等待生效...")
                time.sleep(0.5)
            else:
                日志打印("未找到免费加速按钮，跳过")

        # ========== 第2次识别：找加速按钮 ==========
        日志打印("正在查找加速按钮...")
        按钮位置 = 查找单个匹配(
            屏幕截图(), os.path.join(模板_加速目录, "按钮", "加速按钮.png"), 阈值=0.7
        )
        if not 按钮位置:
            日志打印("未找到加速按钮")
            return
        按钮位置 = 计算偏移位置(*按钮位置)
        日志打印(f"加速按钮位置: {按钮位置}")

        # ========== 按住按钮，按列表拖动 ==========
        bx, by = 按钮位置
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        日志打印(f"已按住加速按钮，开始拖动...")
        time.sleep(0.1)

        for i, (tx, ty) in enumerate(需加速列表):
            偏移位置 = 计算偏移位置(tx, ty)
            mouse.position = 偏移位置
            日志打印(f"经过第 {i + 1} 朵花: {偏移位置}")
            time.sleep(拖动间隔)

        mouse.release(Button.left)
        日志打印(f"=== 加速完成！共加速 {len(需加速列表)} 朵花 ===")

    except KeyboardInterrupt:
        日志打印("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    加速()