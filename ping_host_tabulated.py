import threading
from ipaddress import ip_address
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE

import chardet
from tabulate import tabulate


def ping_ip(address):
    """ Ping an ip address """
    reply = Popen(f'ping {address}', stdout=PIPE, stderr=PIPE)

    # print(reply)
    CODE = reply.wait()
    # print(CODE)
    if CODE == 0:
        print(f"{address}: True")
        return {
            "address": address,
            "result": True,
            "object": reply.stdout
        }
    print(f"{address}: False")
    return {
        "address": address,
        "result": False,
        "object": reply.stderr
    }


def host_ping_tabulated(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        print(tabulate(res, headers='keys'))
        return res
    return wrapper


@host_ping_tabulated
def host_range_ping(address, rnd):
    PROCESS = []
    IP = ip_address(address)
    for i in range(rnd):
        result = ping_ip(f'{IP + i}')
        PROCESS.append(result)
    return PROCESS


host_range_ping('185.185.68.218', 7)
