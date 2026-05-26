# 引入Airtest的图像识别和设备控制库
import sys

from airtest.core.api import *

try:
    # 1. 让脚本在屏幕上寻找所有符合"成熟花朵"特征的位置
    target_list = find_all(Template(r"成熟花朵.png", threshold=0.8))

    if target_list:
        # 2. 触发收花菜单：点击第一朵花
        first_flower = target_list[0]
        touch(first_flower)
        sleep(0.5)

        # 3. 点击弹窗中的"收花"按钮
        if exists(Template(r"收花按钮.png")):
            touch(Template(r"收花按钮.png"))
            sleep(0.2)

            # 4. 开始滑动收割
            swipe_along(target_list)

except KeyboardInterrupt:
    print("\n已停止。")
    sys.exit(0)
