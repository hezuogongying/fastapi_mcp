# backend/core/backend_in_syspath.py
import os
import sys

def ensure_backend_in_syspath(start_path):
    """
    自动回溯查找backend目录，并将其父目录加入sys.path（如已存在则不重复添加）。
    用法：在脚本开头调用 ensure_backend_in_syspath(__file__)
    """
    cur = os.path.abspath(start_path)
    while True:
        if os.path.isdir(os.path.join(cur, "backend")):
            backend_parent = os.path.dirname(os.path.join(cur, "backend"))
            if backend_parent not in sys.path:
                sys.path.insert(0, backend_parent)
            return
        parent = os.path.dirname(cur)
        if parent == cur:
            raise RuntimeError("未找到backend目录")
        cur = parent