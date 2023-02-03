from asyncio import futures
from multiprocessing import Process, Semaphore
import random
import time
import sys
import sysv_ipc
import decimal
from threading import Thread
import socket, os
from _thread import *
from socketserver import ThreadingMixIn
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
from multiprocessing import Process, Value, Lock, Pipe
from weather import update_weather
from external import handle_external
import signal


HOST = "localhost"
PORT = 1792
storage = 1000000
energyTransaction = 0
energyPrice = 0.145 #e/KWh
loop0 = True
loop1 =False
day = 1
temperature = 23


def request_handler(conn, addr):
    global loop0
    while True : 
        data = conn.recv(1024).decode('utf8')
        #print(data)
        if not data:
            print("Bye")
            break
        if data == 'end':
            print("End of transactions with homes\n")
            loop0 = False
            break
        else:
            data = int(data)
            handle_energy(data)
            energyTransaction = energyTransaction + data
            coeffTransaction()
            energyTransaction = 0
    #conn.close()

def priceEnergy():
    global temperature
    global energyPrice
    coeffAtte = 0.99
    coeffWeather = handle_temp(temperature)
    coeffTrans = coeffTransaction()
    coeffEvents = handle_Events()
    energyPrice = (coeffAtte  + coeffTrans  + coeffWeather + coeffEvents) * energyPrice
    return energyPrice


def handle_energy(energy):
    global storage
    global energyTransaction
    storage = storage + energyTransaction
    if energy < 0: #selling energy
        print("Selling %d\n" % -energy)
        storage=storage-energy
    elif energy > 0: #buying energy
        print("Buying %d\n" % energy)
        storage=storage+energy
    elif energy == 0:
        print("No exchange\n")

def handle_temp(temp):
    coeff1=temp-23
    if coeff1 > 0:
        return float(-coeff1*0.01)
    else:
        return float(coeff1*0.01)

def coeffTransaction():
    global energyTransaction
    if energyTransaction > 0:
        #print("Decreasing price!\n")
        return -energyTransaction/1000000
    elif energyTransaction < 0:
        #print("Inscreasing price!\n")
        return energyTransaction/1000000
    else:
        #print("Nothing happened!\n")
        return 0

def handler(sig, frame):
    if sig == signal.SIGUSR1:
        handle_Events()

def handle_Events():
    a = random.random()
    #print(a)
    if 0 <= a < 0.2:
        print("Nothing special!\n")
        return 0
    elif 0.2 <= a < 0.4:
        print("Strikes!\n")
        return a*0.1
    elif 0.4 <= a < 0.6:
        print("Financial aids!\n")
        return -a*0.1
    elif 0.6 <= a < 0.8:
        print("Diplomatic tensions!\n")
        return a*0.1
    else:
        print("Natural disaster!\n")
        return a*0.1
    
if __name__ == "__main__":

    #connect with homes with sockets 
    print("Starting market.\n")
    print("Day 1\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen(10)
            print("Waiting for connections from homes...\n")
            while True:
                while loop0:
                    #print("loop 0")
                    conn, addr = server_socket.accept()
                    futures= [executor.submit(request_handler, conn, addr)]
                    wait(futures)
                    #conn.close()
            
                #print("Done")
                loop1 = True

                while loop1:
                    #process weather
                    parent_conn, child_conn = Pipe()
                    p = Process(target = update_weather, args = (child_conn, temperature))
                    p.start()
                    phrase = input("Tap 'get' to have new updates about temperature: ")
                    while phrase.lower() != "get":
                        phrase = input("Please enter 'get' only at this stage! Tap 'get' again: ")
                    #parent_conn.send("Get")
                    while phrase.lower() != "end":
                        parent_conn.send(phrase)
                        temperature = parent_conn.recv()
                        print("Temperature for the moment is: %d\n" % temperature)
                        handle_temp(temperature)
                        phrase = input("Tap 'get' again to get another update of temperature or 'end' to go for next step: ")
                        while not (phrase.lower() == "get" or phrase.lower() == "end"):
                            phrase = input("Please enter 'get' or 'end' only at this stage! Tap 'get' or 'end' again: ")
                        
                    #process external
                    print("Here is some news:\n")
                    signal.signal(signal.SIGUSR1, handler)
                    ex=Process(target=handle_external)
                    ex.start()
                    ex.terminate()
                    ex.join()

                    #update price energy
                    energyPrice = priceEnergy()
                    print("Energy price at the end of the day %f\n" % energyPrice)

                    #update production ratio to homes
                    value=input("Press 'y' to send new production/consumption ratio to home(s) and skip to next day: ")
                    print()
                    if value == 'y':
                        conn.sendall(str(handle_temp(temperature)).encode())#sending production ratio instead of price
                        updateDay=conn.recv(1024).decode()
                        if not updateDay:
                            break
                        day=int(updateDay)
                        print("Starting new day\n")
                        print("Day %d\n" % day)
                        loop0=True
                        loop1=False
                        break
                    else:
                        conn.sendall("end".encode())
                        print("Thanks for using this simulation")
                        parent_conn.close()
                        child_conn.close()
                        p.terminate()
                        p.join()
                        loop0=False
                        loop1=False
                        # conn.sendall(value.encode())
                        conn.close()
                        server_socket.close()
                        os._exit(os.EX_OK)
