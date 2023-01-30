import random
import sysv_ipc
import socket
import multiprocessing
from home import Home
from multiprocessing import Process


energy_interval = [25, 35] # kWh
homes_list = []

day = 1

total_exchange_homes = 0
total_policy_2 = 0
total_policy_3 = 0
total_exchange_market = 0

# key = 123
# mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
type_policy_1 = 1
type_policy_2 = 2
type_policy_3 = 3
type_need = 4
type_eof = 5

HOST = "localhost"
PORT = 1789


def init_homes_list(no_homes):

    # Initialize homes list
    for i in range(no_homes):
        home = Home(i + 1, random.uniform(energy_interval[0], energy_interval[1]), random.uniform(energy_interval[0], energy_interval[1]), random.randint(1,3))
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
            while gap + float(value) < 0 and type != type_eof:
                gap += float(value)
                message, type = mq.receive(type = -5)
                value = message.decode()
            gap = gap + float(value)
            # print("Send: ",gap, type)
            if gap > 0:
                mq.send(str(gap).encode(), type = type)
                # home.exchange_market = 0
                # home.set_exchange_market(0)
                print(1, gap)
                return home.id, 0
                #break
            else:
                mq.send("0".encode(), type = type_eof)
                # home.exchange_market = gap
                home.set_exchange_market(gap)
                print(2, home.exchange_market, gap)
                return home.id, gap
                # break
        elif gap >= 0:
            mq.send(message, type = type)
            print(3)
            return home.id, home.exchange_market
            # break


def handle_last_receive(home):
    while True:
        if home.trading_policy != 3:
            print("exit")
            return home.id, home.exchange_market
        else:
            message, type = mq.receive(type = -5)
            if type == type_eof:
                mq.send("0".encode(), type = type_eof)
                print("exit")
                return home.id, home.exchange_market
                # break
            while type != type_policy_3:
                if type == type_policy_1:
                    message, type = mq.receive(type = -5)
                if type == type_eof:
                    mq.send("0".encode(), type = type_eof)
                    print("exit")
                    return home.id, home.exchange_market
            # if type == type_policy_3:
            value = message.decode()
            # home.exchange_market = float(value)
            # home.set_exchange_market(float(value))
            print(value)
            return home.id, float(value)
            # break

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
        # pool.map(handle_first_receive, homes_list)
    mq.send("0".encode(), type = type_eof)
    print()

    # Receive first messages from the Message Queue
    # with multiprocessing.Pool(processes = 4) as pool:
    #     pool.map_async(handle_first_receive, homes_list).get()
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


