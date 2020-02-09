import random
import time
from queue import Queue
from threading import Thread, Event, Lock
# ПРИМЕР 1
# class MyThread(Thread):
#     """ Собственный класс потока """
#     def __init__(self, name):
#         super().__init__()
#         self.name = name
#
#     def run(self):
#         amount = random.randint(3, 15)
#         time.sleep(amount)
#         msg = f"Поток {self.name} запущен"
#         print(msg)
#
#
# def create_threads(number):
#     for i in range(number):
#         name = f"Thread {i + 1}"
#         my_thread = MyThread(name)
#         my_thread.start()
#
#
# create_threads(5)

# ПРИМЕР 2
# def writer(message, event_for_wait, event_for_set):
#     """
#     Ф-ия принимает на вход параметр, событие, котрое ожидают и
#     еще одно событие которое необходимо установаить
#     """
#     for i in range(10):
#         # wait for event
#         event_for_wait.wait()
#         # clear event from True to False
#         event_for_wait.clear()
#         print(message)
#         # set True for the next event
#         event_for_set.set()
#
#
# EVENT_1 = Event()
# EVENT_2 = Event()
#
# # Создаем новые потоки от класса Thread
# THR_1 = Thread(target=writer, args=('Я - первый поток', EVENT_2, EVENT_1))
# THR_2 = Thread(target=writer, args=('Я - второй поток', EVENT_1, EVENT_2))
#
# # Запускаем созданные потоки
# THR_1.start()
# THR_2.start()
#
# # Устанавливаем значение True
# EVENT_1.set()
#
# THR_1.join()
# THR_2.join()

# ПРИМЕР 3
# SHARED_RESOURCE_WITH_LOCK = 0
# SHARED_RESOURCE_WITHOUT_LOCK = 0
# COUNT = 100
# SHARED_RESOURCE_LOCK = Lock()
#
#
# def increment_with_lock():
#     """ Инкремент с блокировкой """
#     global SHARED_RESOURCE_WITH_LOCK
#     for i in range(COUNT):
#         SHARED_RESOURCE_LOCK.acquire()
#         SHARED_RESOURCE_WITH_LOCK += 1
#         print(SHARED_RESOURCE_WITH_LOCK)
#         SHARED_RESOURCE_LOCK.release()
#
#
# def decrement_with_lock():
#     """ Декремент с блокировкой """
#     global SHARED_RESOURCE_WITH_LOCK
#     for i in range(COUNT):
#         SHARED_RESOURCE_LOCK.acquire()
#         SHARED_RESOURCE_WITH_LOCK -= 1
#         print(SHARED_RESOURCE_WITH_LOCK)
#         SHARED_RESOURCE_LOCK.release()
#
#
# def increment_without_lock():
#     """ Инкремент без блокировки """
#     global SHARED_RESOURCE_WITHOUT_LOCK
#     for i in range(COUNT):
#         SHARED_RESOURCE_WITHOUT_LOCK += 1
#         print(SHARED_RESOURCE_WITHOUT_LOCK)
#
#
# def decrement_without_lock():
#     """ Декремент без блокировки """
#     global SHARED_RESOURCE_WITHOUT_LOCK
#     for i in range(COUNT):
#         SHARED_RESOURCE_WITHOUT_LOCK -= 1
#         print(SHARED_RESOURCE_WITHOUT_LOCK)
#
#
# if __name__ == "__main__":
#     # THR_1 = Thread(target=increment_with_lock)
#     # THR_2 = Thread(target=decrement_with_lock)
#     THR_3 = Thread(target=increment_without_lock)
#     THR_4 = Thread(target=decrement_without_lock)
#     # THR_1.start()
#     # THR_2.start()
#     THR_3.start()
#     THR_4.start()
#     # THR_1.join()
#     # THR_2.join()
#     THR_3.join()
#     THR_4.join()


# class WorkerThread(Thread):
#     """ поток с очередью """
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.input_queue = Queue()
#
#     def send(self, item):
#         self.input_queue.put(item)
#
#     def close(self):
#         self.input_queue.put(None)
#         self.input_queue.join()
#
#     def run(self):
#         while True:
#             item = self.input_queue.get()
#             if item is None:
#                 break
#             print(item)
#             self.input_queue.task_done()
#         self.input_queue.task_done()
#         return
#
#
# WT_OBJ = WorkerThread()
# WT_OBJ.start()
# WT_OBJ.send('hello')
# WT_OBJ.send('world')
# WT_OBJ.close()

# Пример 3
