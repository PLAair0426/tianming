import sys
import time
import random
import threading

def rpg_typewriter(text, speed=0.03):
    """模拟打字机效果"""
    punctuations = [',', '，', '。', '.', '!', '！', '?', '？', '：', '\n']
    
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        delay = speed
        if char in punctuations:
            delay = speed * 8
        if char == '\n':
            delay = speed * 15
        time.sleep(delay)
    print()

def _loading_animation(stop_event):
    """内部加载动画函数"""
    base_message = "技师在思考中..."
    while not stop_event.is_set():
        dots = "." * random.randint(1, 5)
        sys.stdout.write(f"\r{base_message}{dots}   ")
        sys.stdout.flush()
        time.sleep(0.3)
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()

class LoadingContext:
    """上下文管理器，用于自动处理动画的开启和关闭"""
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=_loading_animation, args=(self.stop_event,))

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()
        self.thread.join()