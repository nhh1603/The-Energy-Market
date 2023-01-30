import random
import sysv_ipc
import socket
import multiprocessing
from home import Home

energy_interval = [20, 40] # kWh
homes_list = []

day = 1

total_exchange_homes = 0
total_policy_2 = 0
total_policy_3 = 0
total_exchange_market = 0

key = 123
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
type_policy_1 = 1
type_policy_2 = 2
type_policy_3 = 3
type_need = 4

HOST = "localhost"
PORT = 1789

def handle_request(home):
    message = str(home.gap).encode()
    if home.gap < 0:
        mq.send(message, type = type_need)
    else:
        if home.trading_policy == 1:
            mq.send(message, type = type_policy_1)
        elif home.trading_policy == 2:
            mq.send(message, type = type_policy_2)
        elif home.trading_policy == 3:
            mq.send(message, type = type_policy_3)

def handle_message_queue(home):
    gap = home.gap
    print("Init: ", gap)
    if gap > 0:
        message = str(gap).encode()
        if home.trading_policy == 1:
            mq.send(message, type = type_policy_1)
        elif home.trading_policy == 3:
            mq.send(message, type = type_policy_3)
    else:
        message, type = mq.receive(type = -3)
        value = message.decode()
        while gap + float(value) < 0:
            gap += float(value)
            message, type = mq.receive(type = -3)
            value = message.decode()
        gap += float(value)
        print("Send: ",gap, type)
        mq.send(str(gap).encode(), type = type)

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

    # Initialize homes list
    for i in range(no_homes):
        home = Home(random.uniform(energy_interval[0], energy_interval[1]), random.uniform(energy_interval[0], energy_interval[1]), random.randint(1,3))
        homes_list.append(home)

    for home in homes_list:
        print(home)

    # Send messages to the Message Queue
    with multiprocessing.Pool(processes = no_homes) as pool:
        pool.map_async(handle_message_queue, homes_list).get()
    #     pool.map_async(handle_request, homes_list).get()
    # mq.send("EOF".encode())
    
    # # Receive messages from the Message Queue
    # while True:
    #     message, t = mq.receive()
    #     value = message.decode()

    #     if value == "EOF":
    #         print("exit")
    #         break

    #     if t != type_policy_2:
    #         total_exchange_homes += float(value)
    #     if t == type_policy_2:
    #         total_policy_2 += float(value)
    #     if t == type_policy_3:
    #         total_policy_3 += float(value)

    #     print(value, t)
        
    mq.remove()

    # Prepare message to send to the market
    if total_exchange_homes >= total_policy_3:
        total_exchange_market = total_policy_3 + total_policy_2
    else:
        total_exchange_market = total_exchange_homes + total_policy_2

    # Homes client socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(str(total_exchange_market).encode())
    # print("Total exchange homes: ", total_exchange_homes)
    # print("Total policy 2: ", total_policy_2)
    # print("Total policy 3: ", total_policy_3)
    # print("Total exchange market: ", total_exchange_market)

    
