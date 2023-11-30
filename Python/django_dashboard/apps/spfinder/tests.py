
import threading

def worker(num):
    """thread worker function"""
    print('Worker: %s' % num)
    print(threading.current_thread().getName())
    return

threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()