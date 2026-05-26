import os

from pynput import keyboard, mouse

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "配置", "配置.txt")
mouse_controller = mouse.Controller()


def replace_section(content, section_name, new_line):
    lines = content.splitlines()
    result = []
    in_section = False
    section_written = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"{section_name}:":
            in_section = True
            result.append(line)
            if not section_written:
                result.append(new_line)
                section_written = True
            continue
        if in_section:
            if ":" in stripped and stripped.endswith(":"):
                in_section = False
                result.append(line)
            else:
                continue
        else:
            result.append(line)
    return "\n".join(result)


def save_pos(x, y):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    content = replace_section(content, "收花按钮", f"{x},{y}")
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"收花按钮位置已保存: ({x}, {y})")


def on_press(key):
    if hasattr(key, "char") and key.char == "1":
        x, y = mouse_controller.position
        save_pos(x, y)
        return False
    elif key == keyboard.Key.esc:
        print("已取消，未保存。")
        return False


print("=== 记录收花按钮 ===")
print("先在游戏中点击花朵让【收花按钮】弹出来")
print("然后将鼠标移到按钮上，按 【1】 记录位置")
print("按 【Esc】 取消")
print("========================")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
