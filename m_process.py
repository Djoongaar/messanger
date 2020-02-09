import multiprocessing
import time

# Пример 1
# def clock(interval):
#     """ Просто функция """
#     while True:
#         print(f"The time is {time.ctime()}")
#         time.sleep(interval)
#
#
# if __name__ == "__main__":
#     PROC = multiprocessing.Process(target=clock, args=(1,))
#     PROC.start()


# class ClockProcess(multiprocessing.Process):
#     """ Простой класс-процесс """
#     def __init__(self, interval):
#         super().__init__()
#         self.interval = interval
#
#     def run(self):
#         while True:
#             print(f"Текущее время: {time.ctime()}")
#             time.sleep(self.interval)
#
#
# if __name__ == "__main__":
#     PROC = ClockProcess(1)
#     PROC.start()

# Пример 2
# def consumer(input_q):
#     while True:
#         print('извлекаю...')
#         item = input_q.get()
#         print(item)
#         input_q.task_done()
#         time.sleep(1)
#
#
# def producer(sequence_obj, output_q):
#     """ Производитель добавляет элементы в очередь """
#     for item in sequence_obj:
#         print('помещаю...')
#         output_q.put(item)
#         time.sleep(1)
#
#
# if __name__ == "__main__":
#     """ Создаем процесс очереди, доступный для совместного использования """
#     QUEUE = multiprocessing.JoinableQueue()
#     # Создать процесс-потребитель
#     CONSUMER_PROCESS = multiprocessing.Process(target=consumer, args=(QUEUE,))
#     CONSUMER_PROCESS.daemon = True
#     CONSUMER_PROCESS.start()
#
#     # Элементы которые будет получать потребитель для обработки
#     SEQUENCE = [1, 2, 4, 3, 1]
#     # Запуск функции производителя
#     producer(SEQUENCE, QUEUE)
#     QUEUE.join()
