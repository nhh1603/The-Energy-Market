import random
import sysv_ipc
import socket
import multiprocessing
from home import Home
from multiprocessing import Process


energy_interval = [25000, 35000] # Wh
homes_list = []

day = 1

type_policy_1 = 1
type_policy_3 = 3
type_eof = 5

HOST = "localhost"
PORT = 1789


# Initialize homes list when start the program
def init_homes_list(no_homes):

    # Initialize homes list
    for i in range(no_homes):
        home = Home(i + 1, random.randint(energy_interval[0], energy_interval[1]), random.randint(energy_interval[0], energy_interval[1]), random.randint(1,3))
        homes_list.append(home)

    for home in homes_list:
        print(home)


def handle_first_send(home):
    message = str(home.gap).encode()
    if home.gap > 0:
        if home.trading_policy == 1:
            mq.send(message, type = type_policy_1)
        elif home.trading_policy == 3:
            mq.send(message, type = type_policy_3)
    

def handle_first_receive(home):
    while True:
        gap = home.gap
        message, type = mq.receive(type = -5)
        value = message.decode()
        if type == type_eof:
            mq.send("0".encode(), type = type_eof)
            print("exit")
            return home.id, home.exchange_market
            # break
        if gap < 0:
            while gap + int(value) < 0 and type != type_eof:
                gap += int(value)
                message, type = mq.receive(type = -5)
                value = message.decode()
            gap = gap + int(value)
            # print("Send: ",gap, type)
            if gap > 0:
                mq.send(str(gap).encode(), type = type)
                return home.id, 0
            else:
                mq.send("0".encode(), type = type_eof)
                return home.id, gap
        elif gap >= 0:
            mq.send(message, type = type)
            return home.id, home.exchange_market


def handle_last_receive(home):
    while True:
        if home.trading_policy != 3:
            return home.id, home.exchange_market
        else:
            message, type = mq.receive(type = -5)
            if type == type_eof:
                mq.send("0".encode(), type = type_eof)
                return home.id, home.exchange_market
                # break
            while type != type_policy_3:
                if type == type_policy_1:
                    message, type = mq.receive(type = -5)
                if type == type_eof:
                    mq.send("0".encode(), type = type_eof)
                    return home.id, home.exchange_market
            value = message.decode()
            return home.id, int(value)


if __name__ == '__main__':

    # Input the number of homes
    while True:
        no_homes = input("Please enter number of homes: ")
        if no_homes.isdigit():
            no_homes = int(no_homes)
            if no_homes > 0:
                break
            else:
                print("Please enter a positive integer!")
        else:
            print("Please enter an integer!")

    init_homes_list(no_homes)

    key = 123
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

    # Send first messages to the Message Queue
    with multiprocessing.Pool(processes = 4) as pool:
        pool.map(handle_first_send, homes_list)
    mq.send("0".encode(), type = type_eof)
    print()

    # Receive first messages from the Message Queue
    with multiprocessing.Pool(processes = 4) as pool:
        for result in pool.map_async(handle_first_receive, homes_list).get():
            homes_list[result[0]-1].exchange_market = result[1]
    print()

    # Receive last messages from the Message Queue
    with multiprocessing.Pool(processes = 4) as pool:
        for result in pool.map_async(handle_last_receive, homes_list).get():
            homes_list[result[0]-1].exchange_market = result[1]
    print()
    mq.remove()

    for home in homes_list:
        print(home.exchange_market)


