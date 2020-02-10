""" Лаунчер """

import subprocess

PROCESS = []

while True:
    ACTION = input('Выберите действие: '
                   '\nq - выход, '
                   '\ns - запустить сервер и клиенты, '
                   '\nx - закрыть все окна: ')
    if ACTION == 'q':
        break

    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python client.py -n EUGENE', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python client.py -n LYUBA', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python client.py -n VASYA', creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
