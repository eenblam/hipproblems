import threading

class SafeStack(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.stack = []

    def pop(self):
        self.lock.acquire()
        try:
            item = self.stack.pop()
        finally:
            self.lock.release()
        return item

    def push(self, item):
        self.lock.acquire()
        try:
            self.stack.append(item)
        finally:
            self.lock.release()
