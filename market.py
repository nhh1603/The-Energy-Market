from multiprocessing import Process, Semaphore
import random
import time
import sys
import sysv_ipc
import decimal
import threading
import socket
from _thread import *

HOST = "localhost"
PORT = 1789
lock = threading.Lock()
storage = 1000000
energyTransaction = 0
energyPrice = 0.145 #e/KWh
#functions

def priceEnergy():
    global energyPrice
    coeffAtte = 0.99
	#coeffWeather = weather()
    coeffTrans = coeffTransaction()
    energyPrice = coeffAtte * energyPrice + coeffTrans * energyPrice
    return energyPrice

def handle_energy(energy):
    global storage
    global energyTransaction
    storage = storage + energyTransaction
    if energy < 0: #selling energy
        print("Selling %d" % -energy)
        storage=storage-energy
    elif energy > 0: #buying energy
        print("Buying %d" % energy)
        storage=storage+energy
    elif energy == 0:
        print("Nothing happened")

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

#def weather(): shared memory

def multi_threaded_client(connection):
    global energyTransaction
    global energyPrice
    while True:
        data = connection.recv(1024).decode()
        if not data:
            #print("Bye")
            lock.release()
            break
        data = int(data)
        print(data)
        handle_energy(data)
        energyTransaction = energyTransaction + data
        coeffTransaction()
        energyPrice = priceEnergy()
        energyTransaction = 0
        print("Energy price %f\n" % energyPrice)
    
if __name__ == "__main__":
    #connect with homes with sockets 
    print("Starting market.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    print('Socket is listening..')
    server_socket.listen(5)
    while True:
        client_socket, addr = server_socket.accept()
        lock.acquire()
        print('Connected to: ' + addr[0] + ':' + str(addr[1]))
        start_new_thread(multi_threaded_client, (client_socket, ))
        #value=input("Press y to send energy price to home(s) and continue this simulation\n")
        #if value == 'y':    
        #    client_socket.sendall(energyPrice)
        #else:
        #    print("Thanks for using this simulation")
    
    server_socket.close()