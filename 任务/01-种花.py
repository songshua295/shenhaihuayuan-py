import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pynput import keyboard
from pynput.mouse import Button, Controller
from pypinyin import lazy_pinyin

from 工具.图像识别 import 屏幕截图, 查找单个匹配, 查找所有匹配
from 工具.读取配置 import 计算偏移位置, 读取配置
from 工具.日志打印 import 日志打印, 启动日志线程

mouse = Controller()

模板_花种目录 = os.path.join(
    os.path.dirname(__file__), "..", "素材", "01-种花模板", "模板"
)
模板_空地 = os.path.join(
    os.path.dirname(__file__), "..", "素材", "01-种花模板", "空地", "0空地.png"
)
模板_其他素材 = os.path.join(
    os.path.dirname(__file__), "..", "素材", "01-种花模板", "其他素材"
)

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

def 列出花种():
    种子列表 = []
    for f in sorted(os.listdir(模板_花种目录)):
        if f.endswith(".png"):
            种子列表.append(f.replace(".png", ""))
    return 种子列表

def 获取拼音首字母(中文名):
    return "".join([p[0] for p in lazy_pinyin(中文名)])

全量种子 = 列出花种()
拼音索引 = {name: 获取拼音首字母(name) for name in 全量种子}

def 选择花种():
    if not 全量种子:
        日志打印("错误：花种模板目录为空，请放入花种图片")
        return None

    当前列表 = 全量种子

    while True:
        日志打印(f"\n可选花种（共 {len(当前列表)} 种）：")
        for i, name in enumerate(当前列表):
            日志打印(f"  [{i + 1}] {name}")

        提示 = f"\n输入序号直接选，或输入拼音首字母过滤（如 xrk→向日葵），直接回车重新显示全部："
        choice = input(提示).strip()

        if not choice:
            当前列表 = 全量种子
            continue

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(当前列表):
                选中 = 当前列表[idx]
                路径 = os.path.join(模板_花种目录, f"{选中}.png")
                日志打印(f"已选择：{选中}")
                return 路径, 选中
            日志打印(f"请输入 1~{len(当前列表)} 之间的数字")
            continue

        过滤结果 = [name for name in 全量种子 if choice.lower() in 拼音索引[name]]
        if not 过滤结果:
            日志打印(f"未找到拼音首字母匹配「{choice}」的花种")
            当前列表 = 全量种子
        elif len(过滤结果) == 1:
            选中 = 过滤结果[0]
            路径 = os.path.join(模板_花种目录, f"{选中}.png")
            日志打印(f"自动选择唯一匹配：{选中}")
            return 路径, 选中
        else:
            当前列表 = 过滤结果

def 尝试进入种植界面():
    种植界面模板 = os.path.join(模板_其他素材, "种植界面.png")
    if os.path.exists(种植界面模板):
        位置 = 查找单个匹配(屏幕截图(), 种植界面模板, 阈值=0.7)
        if 位置:
            mouse.position = 位置
            mouse.click(Button.left, 1)
            日志打印(f"✅ 已点击种植界面按钮 {位置}")
            time.sleep(1)
            return True

    空地列表 = 查找所有匹配(屏幕截图(), 模板_空地, 阈值=0.75)
    if 空地列表:
        位置 = 空地列表[0]
        mouse.position = 位置
        mouse.click(Button.left, 1)
        日志打印(f"✅ 已点击空地 {位置}，进入种植界面")
        time.sleep(1)
        return True

    return False

def 种花():
    启动日志线程()
    日志打印("=== 种花 ===")

    花种结果 = 选择花种()
    if not 花种结果:
        return
    花种模板路径, 花种名称 = 花种结果

    日志打印(f"\n正在识别花种位置...")
    花种位置 = 查找单个匹配(屏幕截图(), 花种模板路径, 阈值=0.7)

    if not 花种位置:
        日志打印(f"未直接找到【{花种名称}】，尝试进入种植界面...")
        if 尝试进入种植界面():
            日志打印("重新识别花种位置...")
            花种位置 = 查找单个匹配(屏幕截图(), 花种模板路径, 阈值=0.7)

        下一页模板 = os.path.join(模板_其他素材, "种植界面-下一页.png")
        for 翻页次 in range(1, cfg.get("种花最大翻页次数", 5) + 1):
            if 花种位置:
                break
            if not os.path.exists(下一页模板):
                break
            下一页位置 = 查找单个匹配(屏幕截图(), 下一页模板, 阈值=0.7)
            if not 下一页位置:
                日志打印("没有下一页了")
                break
            mouse.position = 下一页位置
            mouse.click(Button.left, 1)
            日志打印(f"翻到第 {翻页次 + 1} 页 {下一页位置}")
            time.sleep(1)
            花种位置 = 查找单个匹配(屏幕截图(), 花种模板路径, 阈值=0.7)

        if not 花种位置:
            日志打印(f"仍未找到【{花种名称}】，放弃")
            return

    花种位置 = 计算偏移位置(*花种位置)
    日志打印(f"【{花种名称}】位置: {花种位置}")

    # print(f"\n2 秒后开始执行...（按 Esc 或 Ctrl+C 停止）")
    # time.sleep(2)

    try:
        sx, sy = 花种位置
        mouse.position = (sx, sy)
        time.sleep(0.1)
        mouse.press(Button.left)
        日志打印(f"已按住【{花种名称}】，开始扫描空地并拖动...")
        time.sleep(0.2)

        已种植数 = 0
        while True:
            if 最大上限 > 0 and 已种植数 >= 最大上限:
                日志打印(f"已达到上限 {最大上限}，停止")
                break

            当前截图 = 屏幕截图()
            当前空地 = 查找所有匹配(当前截图, 模板_空地, 阈值=0.75)

            if not 当前空地:
                日志打印("所有空地已种完！")
                break

            鼠标位置 = mouse.position
            最近空地 = min(
                当前空地,
                key=lambda p: (p[0] - 鼠标位置[0]) ** 2 + (p[1] - 鼠标位置[1]) ** 2,
            )
            最近空地 = 计算偏移位置(*最近空地)

            mouse.position = 最近空地
            已种植数 += 1
            日志打印(f"已种 {已种植数}: 拖动到空地 ({最近空地[0]}, {最近空地[1]})")
            time.sleep(拖动间隔)

        mouse.release(Button.left)
        日志打印(f"=== 【{花种名称}】种植完成！共种植 {已种植数} 块空地 ===")

    except KeyboardInterrupt:
        日志打印("\n已停止（Ctrl+C），鼠标已释放。")


if __name__ == "__main__":
    种花()