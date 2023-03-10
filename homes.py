import random
import sysv_ipc
import socket
import multiprocessing
from home import Home
from multiprocessing import Process
from multiprocessing import Pool
import os

key = 123
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

energy_interval = [25000, 35000] # Wh
homes_list = []

day = 1

type_policy_1 = 1
type_policy_3 = 3
type_eof = 5

HOST = "localhost"
PORT = 1794

loop = True


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
            return home.id, home.exchange_market
        if gap < 0:
            while gap + int(value) < 0 and type != type_eof:
                gap += int(value)
                message, type = mq.receive(type = -5)
                value = message.decode()
            gap = gap + int(value)
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
            while type != type_policy_3:
                if type == type_policy_1:
                    message, type = mq.receive(type = -5)
                if type == type_eof:
                    mq.send("0".encode(), type = type_eof)
                    return home.id, home.exchange_market
            value = message.decode()
            return home.id, int(value)


def handle_client_server(home):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(str(home.exchange_market).encode('utf8'))

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
    print("Starting homes...\n")

    init_homes_list(no_homes)

    mq.send("0".encode(), type = type_eof)

    while True:
        # Send first messages to the Message Queue
        with multiprocessing.Pool(processes = 8) as pool:
            pool.map(handle_first_send, homes_list)
        print()

        # Receive first messages from the Message Queue
        with multiprocessing.Pool(processes = 8) as pool:
            for result in pool.map_async(handle_first_receive, homes_list).get():
                homes_list[result[0]-1].exchange_market = result[1]

        # Receive last messages from the Message Queue
        with multiprocessing.Pool(processes = 8) as pool:
            for result in pool.map_async(handle_last_receive, homes_list).get():
                homes_list[result[0]-1].exchange_market = result[1]

        # Client server

        print("Energy remaining after exchanges between homes, which will be used to exchange with market\n")

        for home in homes_list:
            print(f"Home {home.id}: {home.exchange_market} Wh")

        print()

        with multiprocessing.Pool(processes = 8) as pool:
            clients=pool.map_async(handle_client_server, homes_list)
            clients.wait()

        loop=True
        
        while loop:
            update = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            update.connect((HOST, PORT))
            update.send("end".encode())
            data1=update.recv(1024).decode()
            if not data1:
                break
            if data1 == "end":
                print("Thanks for using this simulation!")
                update.close()
                os._exit(os.EX_OK)
            else :
                data1=float(data1)
                for h in homes_list:
                    h.update_home(data1, -data1)
                day=day+1
                print("Starting new day...\n")
                print("Day %d\n" % day)
                update.sendall(str(day).encode())
                for h in homes_list:
                    print(h)
                loop = False
                break


