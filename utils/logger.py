import threading
import time


class Logger:
    def __init__(self):
        self._lock = threading.Lock()
        self._t0 = time.time()

    def log(self, msg: str):
        with self._lock:
            dt = time.time() - self._t0
            thread_name = threading.current_thread().name
            print(f"[{dt:8.3f}s] [{thread_name:12}] {msg}")
