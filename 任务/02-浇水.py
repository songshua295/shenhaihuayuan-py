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

模板_浇水目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "02-浇水")
模板_需要浇水 = os.path.join(os.path.dirname(__file__), "..", "素材", "02-浇水", "模板")
模板_浇水排除 = os.path.join(os.path.dirname(__file__), "..", "素材", "02-浇水", "浇水排除")

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
    启动日志线程()
    日志打印("=== 浇水 ===")

    # 第1次扫描：找需要浇水的花
    需要浇水列表 = 查找所有匹配_多模板(屏幕截图(), 模板_需要浇水, 阈值=0.75)

    if not 需要浇水列表:
        日志打印("未找到需要浇水的花")
        return

    if 最大上限 > 0:
        需要浇水列表 = 需要浇水列表[:最大上限]

    日志打印(f"识别到 {len(需要浇水列表)} 朵需要浇水的花")
    for i, pos in enumerate(需要浇水列表):
        日志打印(f"  第 {i + 1} 朵: {pos}")

    try:
        # 点击第一朵花，触发弹窗
        first = 需要浇水列表[0]
        first = 计算偏移位置(*first)
        mouse.position = first
        mouse.click(Button.left, 1)
        日志打印(f"已点击第一朵花 {first}，等待弹窗...")
        time.sleep(0.8)

        # 找浇水按钮
        日志打印("正在查找浇水按钮...")
        浇水按钮 = 查找单个匹配(
            屏幕截图(), os.path.join(模板_浇水目录, "浇水按钮.png"), 阈值=0.7
        )
        if not 浇水按钮:
            日志打印("未找到浇水按钮")
            return
        浇水按钮 = 计算偏移位置(*浇水按钮)
        日志打印(f"浇水按钮位置: {浇水按钮}")

        # 按住浇水按钮
        bx, by = 浇水按钮
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        日志打印(f"已按住浇水按钮，开始扫描并拖动...")
        time.sleep(0.2)

        # 实时扫描：边拖边截图
        已浇数 = 0
        while True:
            if 最大上限 > 0 and 已浇数 >= 最大上限:
                日志打印(f"已达到上限 {最大上限}，停止")
                break

            当前截图 = 屏幕截图()
            当前需要浇水 = 查找所有匹配_多模板(当前截图, 模板_需要浇水, 阈值=0.7)

            if not 当前需要浇水:
                日志打印("所有需要浇水的花已浇完！")
                break

            # 检查排除模板位置
            当前排除模板 = 查找所有匹配_多模板(当前截图, 模板_浇水排除, 阈值=0.7) if os.path.exists(模板_浇水排除) else []

            鼠标位置 = mouse.position
            while 当前需要浇水:
                最近花 = min(
                    当前需要浇水,
                    key=lambda p: (p[0] - 鼠标位置[0]) ** 2 + (p[1] - 鼠标位置[1]) ** 2,
                )

                # 检查最近花是否被排除
                被排除 = any(
                    abs(最近花[0] - ex[0]) < 30 and abs(最近花[1] - ex[1]) < 30
                    for ex in 当前排除模板
                )

                if 被排除:
                    日志打印(f"  跳过排除位置 ({最近花[0]}, {最近花[1]})")
                    当前需要浇水.remove(最近花)
                else:
                    break

            if not 当前需要浇水:
                日志打印("剩余花已被全部排除，结束")
                break

            最近花 = 计算偏移位置(*最近花)

            mouse.position = 最近花
            已浇数 += 1
            日志打印(f"已浇 {已浇数}: 拖动到 ({最近花[0]}, {最近花[1]})")
            time.sleep(拖动间隔)

        mouse.release(Button.left)
        日志打印(f"=== 浇水完成！共浇 {已浇数} 朵花 ===")

    except KeyboardInterrupt:
        日志打印("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    浇水()