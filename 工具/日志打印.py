"""异步日志打印模块：将日志放入后台线程处理，不阻塞主流程"""

import threading
import time
from collections import deque

_日志队列 = deque()
_队列锁 = threading.Lock()
_日志线程 = None


def 日志打印(*args, **kwargs):
    """将日志加入队列，由后台线程异步输出，不阻塞调用方"""
    with _队列锁:
        _日志队列.append((args, kwargs))


def _日志工作线程():
    while True:
        while _日志队列:
            with _队列锁:
                args, kwargs = _日志队列.popleft()
            print(*args, **kwargs)
        time.sleep(0.01)


def 启动日志线程():
    global _日志线程
    if _日志线程 is None or not _日志线程.is_alive():
        _日志线程 = threading.Thread(target=_日志工作线程, daemon=True)
        _日志线程.start()