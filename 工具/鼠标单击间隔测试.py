"""鼠标双击间隔测试脚本：记录两次单击之间的时间间隔"""

import time

from pynput import mouse


def 开始测试():
    print("=== 鼠标双击间隔测试 ===")
    print("左键单击任意位置，记录两次单击之间的秒数")
    print("按 Esc 或右键单击退出\n")

    上次时间 = None
    点击次数 = 0

    def on_click(x, y, button, pressed):
        nonlocal 上次时间, 点击次数

        if not pressed:
            return

        if button == mouse.Button.right:
            return False

        now = time.perf_counter()
        点击次数 += 1

        if 上次时间 is not None:
            间隔 = now - 上次时间
            print(f"第 {点击次数} 次单击 | 间隔: {间隔:.4f} 秒 ({间隔*1000:.1f} 毫秒)")

        上次时间 = now

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    print("\n测试结束")


if __name__ == "__main__":
    开始测试()