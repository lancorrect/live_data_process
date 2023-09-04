from queue import Queue
from threading import Thread
import random
import time
''' 
python内置的线程安全队列模块queue
'''

# queue = Queue(5)  # 队列用Queue来初始化，里面的数字代表最多几个元素
# for num in range(5):
#     queue.put(num) # put()将一个数据放到队列中

# print(queue.empty())  # 判断队列是否为空
# print(queue.full())  # 判断队列是否满了
# print(queue.qsize())  # 队列大小

# for _ in range(5):
#     num = queue.get() # get()从队列中获取先插入的数据
#     print(num)
# print(queue.empty())  # 判断队列是否为空
# print(queue.full())  # 判断队列是否满了

def put_data(queue, set_num):
    for i in range(set_num):
        queue.put(i)
        # time.sleep(5)

def put_data_random(thread_id, queue):
    while True:
        if queue.full():
            break
        queue.put(random.randint(10,100))
        time.sleep(1)
        print(f"Thread-{thread_id} {queue.qsize()}")

def get_data(thread_id, queue):
    max_retry_times = 10
    cur_retry_time = 0
    while True:
        if queue.empty():
            if cur_retry_time >= 5:
                break
            cur_retry_time += 1
            time.sleep(2)
        else:
            print(f"Thread-{thread_id} gets {queue.get()}")
            time.sleep(1)

queue = Queue(20)
# put_data(queue, 20)
l_put = []
l_get = []
for i in range(5):
    l = Thread(target=put_data_random, args=(i+1, queue))
    l_put.append(l)

for l in l_put:
    l.start()
for l in l_put:
    l.join()

# 当放入数据的线程在前面join的话，输出数据的线程就不会在所有线程结束时启动
# time.sleep(10)
for i in range(5):
    l = Thread(target=get_data, args=(i+1, queue))
    l_get.append(l)

for l in l_get:
    l.start()
for l in l_get:
    l.join()

# for l in l_put:
#     l.start()
# for l in l_get:
#     l.start()

# for l in l_put:
#     l.join()
# for l in l_get:
#     l.join()