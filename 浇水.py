import os
import sys
import threading
import time

from pynput import keyboard
from pynput.mouse import Button, Controller

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "配置", "配置.txt")
mouse = Controller()


# 后台 Esc 监听
def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 读取配置():
    if not os.path.exists(CONFIG_PATH):
        print(f"错误：找不到 {CONFIG_PATH}")
        return None, None

    flowers = []
    water_pos = None
    current_section = None

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line == "花朵坐标:":
                current_section = "flower"
            elif line == "花种位置:":
                current_section = "seed"
            elif line == "收花按钮:":
                current_section = "button"
            elif line == "浇水按钮:":
                current_section = "water"
            elif current_section == "flower":
                try:
                    x, y = line.split(",")
                    flowers.append((int(x), int(y)))
                except ValueError:
                    pass
            elif current_section == "water":
                try:
                    x, y = line.split(",")
                    water_pos = (int(x), int(y))
                except ValueError:
                    pass

    return flowers, water_pos


def 等待按G校准():
    """用户将鼠标移到实际第一朵花位置，按 G 键确认"""

    def on_press(key):
        if hasattr(key, "char") and key.char == "g":
            print(f"已获取实际第一朵花位置: {mouse.position}")
            return False

    print("请将鼠标移到游戏中实际的第一朵花位置，然后按 【G】 键确认校准")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
    return mouse.position


def 浇水():
    flowers, water_pos = 读取配置()

    if not flowers:
        print("错误：没有花朵坐标，请先运行 工具/采集所有花朵田定位.py")
        return
    if not water_pos:
        print("错误：没有浇水按钮位置，请先运行 工具/采集浇水按钮定位.py")
        return

    first_x, first_y = flowers[0]
    print(f"花朵数量: {len(flowers)}")
    print(f"记录的第一朵花位置: ({first_x}, {first_y})")
    print(f"记录浇水按钮位置: {water_pos}")

    # 光标定位
    mouse.position = (first_x, first_y)
    print(f"鼠标已移到记录的位置，请确认并调整到实际花朵位置...")
    time.sleep(1)

    # 等待按 G 校准
    clicked = 等待按G校准()
    偏移_x = clicked[0] - first_x
    偏移_y = clicked[1] - first_y
    实际浇水 = (water_pos[0] + 偏移_x, water_pos[1] + 偏移_y)
    print(f"偏移量: ({偏移_x}, {偏移_y})")
    print(f"修正后浇水按钮位置: {实际浇水}")

    print("1 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(1)

    try:
        # 1. 点击实际第一朵花，触发弹窗
        mouse.position = clicked
        mouse.click(Button.left, 1)
        print(f"点击第一朵花 {clicked}，等待弹窗...")
        time.sleep(1.0)

        # 2. 移到修正后的浇水按钮位置，按住
        wx, wy = 实际浇水
        mouse.position = (wx, wy)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"在浇水按钮 ({wx}, {wy}) 按住鼠标")
        time.sleep(0.1)

        # 3. 拖动经过所有花（偏移修正）
        print("开始拖动...")
        for i, (tx, ty) in enumerate(flowers):
            实际位置 = (tx + 偏移_x, ty + 偏移_y)
            mouse.position = 实际位置
            print(f"经过第 {i + 1} 朵花: {实际位置}")
            time.sleep(0.2)

        # 4. 松开
        mouse.release(Button.left)
        print("=== 浇水完成！ ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    浇水()
