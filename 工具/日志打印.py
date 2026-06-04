"""可配置的异步/同步日志打印模块：支持选择是否将日志放入后台线程处理"""

import threading
import time
from collections import deque

# 配置项：是否使用异步模式（默认为True，即异步模式）
USE_ASYNC_LOGGING = False

_日志队列 = deque()
_队列锁 = threading.Lock()
_日志线程 = None

def 日志打印(*args, **kwargs):
    """日志打印函数: 根据 USE_ASYNC_LOGGING 配置决定同步或异步输出"""
    if USE_ASYNC_LOGGING:
        # 异步模式：将日志加入队列，由后台线程处理
        with _队列锁:
            _日志队列.append((args, kwargs))
    else:
        # 同步模式：直接打印，不阻塞调用方
        print(*args, **kwargs)

def _日志工作线程():
    while True:
        while _日志队列:
            with _队列锁:
                args, kwargs = _日志队列.popleft()
            print(*args, **kwargs)
        time.sleep(0.01)

def 启动日志线程():
    """只在异步模式下启动日志线程"""
    global _日志线程
    if USE_ASYNC_LOGGING:
        if _日志线程 is None or not _日志线程.is_alive():
            _日志线程 = threading.Thread(target=_日志工作线程, daemon=True)
            _日志线程.start()