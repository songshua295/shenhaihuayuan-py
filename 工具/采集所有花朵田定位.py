import os

from pynput import keyboard, mouse

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "配置", "配置.txt")

flowers = []
mouse_controller = mouse.Controller()


def replace_section(content, section_name, new_lines):
    """替换配置文件中某个区域的内容"""
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
                for nl in new_lines:
                    result.append(nl)
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


def save_flowers():
    if not flowers:
        print("未记录到任何坐标，文件未保存。")
        return

    if not os.path.exists(CONFIG_PATH):
        print(f"错误：找不到 {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_lines = [f"{x},{y}" for x, y in flowers]
    content = replace_section(content, "花朵坐标", new_lines)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"成功保存 {len(flowers)} 个花朵坐标到 {CONFIG_PATH}")


def on_press(key):
    global flowers
    if hasattr(key, "char") and key.char == "1":
        x, y = mouse_controller.position
        flowers.append((x, y))
        print(f"已记录第 {len(flowers)} 朵花: ({x}, {y})")
    elif key == keyboard.Key.esc:
        print("\n正在保存...")
        save_flowers()
        return False


print("=== 记录花朵 ===")
print("鼠标滑到花朵上按 【1】 记录，按 【Esc】 保存退出")
print("（每次运行会覆盖之前的记录）")
print("========================")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
