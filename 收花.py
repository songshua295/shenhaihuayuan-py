import os
import sys
import threading
import time

from pynput import keyboard
from pynput.mouse import Button, Controller

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "配置", "配置.txt")
mouse = Controller()
校准完成 = False
实际第一朵花位置 = None


# 后台 Esc 监听（随时按 Esc 停止）
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
        return None, None, None, None

    flowers = []
    btn_pos = None
    seed_pos = None
    water_pos = None
    speed_pos = None
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
            elif line == "加速按钮:":
                current_section = "speed"
            elif current_section == "flower":
                try:
                    x, y = line.split(",")
                    flowers.append((int(x), int(y)))
                except ValueError:
                    pass
            elif current_section == "button":
                try:
                    x, y = line.split(",")
                    btn_pos = (int(x), int(y))
                except ValueError:
                    pass

    return flowers, btn_pos, seed_pos, water_pos, speed_pos


def 等待按G校准():
    """用户将鼠标移到实际第一朵花位置，按 G 键确认"""
    global 校准完成, 实际第一朵花位置

    def on_press(key):
        global 校准完成, 实际第一朵花位置
        if hasattr(key, "char") and key.char == "g":
            实际第一朵花位置 = mouse.position
            校准完成 = True
            return False  # 停止监听

    print("请将鼠标移到游戏中实际的第一朵花位置，然后按 【G】 键确认校准")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    print(f"已获取实际第一朵花位置: {实际第一朵花位置}")
    return 实际第一朵花位置


def 收花():
    global 校准完成, 实际第一朵花位置

    flowers, btn_pos, _, _, _ = 读取配置()

    if not flowers:
        print("错误：没有花朵坐标，请先运行 工具/采集所有花朵田定位.py")
        return
    if not btn_pos:
        print("错误：没有收花按钮位置，请先运行 工具/采集收花按钮定位.py")
        return

    first_x, first_y = flowers[0]
    print(f"花朵数量: {len(flowers)}")
    print(f"记录的第一朵花位置: ({first_x}, {first_y})")
    print(f"记录收花按钮位置: {btn_pos}")

    # 光标定位：鼠标移到记录的第一朵花位置，方便用户找到位置
    mouse.position = (first_x, first_y)
    print(f"鼠标已移到记录的位置，请确认并调整到实际花朵位置...")
    time.sleep(1)

    # 等待用户按 G 键确认实际位置
    clicked = 等待按G校准()
    偏移_x = clicked[0] - first_x
    偏移_y = clicked[1] - first_y

    # 修正按钮位置
    实际按钮 = (btn_pos[0] + 偏移_x, btn_pos[1] + 偏移_y)
    print(f"偏移量: ({偏移_x}, {偏移_y})")
    print(f"修正后收花按钮位置: {实际按钮}")

    print("1 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    time.sleep(1)

    try:
        # 1. 点击实际第一朵花，触发弹窗
        mouse.position = clicked
        mouse.click(Button.left, 1)
        print(f"点击第一朵花 {clicked}，等待弹窗...")
        time.sleep(0.5)

        # 2. 移到修正后的收花按钮位置，按住
        bx, by = 实际按钮
        mouse.position = (bx, by)
        time.sleep(0.1)
        mouse.press(Button.left)
        print(f"在收花按钮 ({bx}, {by}) 按住鼠标")
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
        print("=== 收割完成！ ===")

    except KeyboardInterrupt:
        print("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    收花()
