import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配

mouse = Controller()

模板目录 = os.path.join(os.path.dirname(__file__), "..", "素材", "08-顾客订单")


def _启动停止监听():
    def on_press(key):
        if key == keyboard.Key.esc:
            mouse.release(Button.left)
            os._exit(0)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


threading.Thread(target=_启动停止监听, daemon=True).start()


def 点击模板(文件名, 描述, 等待=1.0):
    路径 = os.path.join(模板目录, 文件名)
    if not os.path.exists(路径):
        return False

    print(f"  正在查找【{描述}】...")
    位置 = 查找单个匹配(屏幕截图(), 路径, 阈值=0.7)
    if not 位置:
        return False

    mouse.position = 位置
    mouse.click(Button.left, 1)
    print(f"  ✅ 已点击【{描述}】{位置}")
    time.sleep(等待)
    return True


def 交付流程():
    点击模板("交付前的确定.png", "交付前的确定", 等待=1.0)
    点击模板("交付.png", "交付", 等待=1.0)
    点击模板("点击任意空白处关闭.png", "任意空白处关闭", 等待=0.5)


def 处理一个订单():
    if 点击模板("花瓶已制作好的.png", "花瓶已制作好的", 等待=1.0):
        print("  → 已制作好，直接交付")
        交付流程()
        return True

    if 点击模板("不可制作花瓶的.png", "不可制作花瓶的", 等待=1.0):
        print("  → 缺货处理")
        点击模板("暂时没货.png", "暂时没货", 等待=1.0)
        return True

    if 点击模板("可制作花瓶的.png", "可制作花瓶的", 等待=1.5):
        print("  → 需要制作")
        点击模板("前往制作.png", "前往制作", 等待=1.5)
        点击模板("制作.png", "制作", 等待=2.0)
        交付流程()
        return True

    return False


def 统计顾客数():
    截图 = 屏幕截图()
    总数 = 0
    for 文件名 in ["花瓶已制作好的.png", "不可制作花瓶的.png", "可制作花瓶的.png"]:
        路径 = os.path.join(模板目录, 文件名)
        if os.path.exists(路径):
            匹配数 = len(查找所有匹配(截图, 路径, 阈值=0.7))
            总数 += 匹配数
            状态 = 文件名.replace(".png", "")
            if 匹配数 > 0:
                print(f"  {状态}: {匹配数} 个")
    return 总数


def 顾客订单():
    print("=== 顾客订单 ===")

    print("正在统计顾客订单数量...")
    顾客数 = 统计顾客数()

    if 顾客数 == 0:
        print("没有找到任何顾客订单")
        return

    print(f"\n共有 {顾客数} 个顾客订单，开始逐个处理")

    for 次 in range(1, 顾客数 + 1):
        print(f"\n--- 处理第 {次}/{顾客数} 个订单 ---")
        if not 处理一个订单():
            print(f"第 {次} 个订单处理失败，停止")
            break

    print(f"\n=== 顾客订单完成！共处理 {次} 个订单 ===")


if __name__ == "__main__":
    顾客订单()
