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

#functions

def priceEnergy():
    energyPrice = 0.145 #e/KWh
    coeffAtte = 0.99
	#coeffWeather = weather()
    coeffTrans = coeffTransaction()
    energyPrice = coeffAtte * energyPrice + coeffTrans * energyPrice
    return energyPrice

def handle_energy(energy):
    global storage
    storage = 1000000#W
    global energyTransaction
    energyTransaction = 0
    storage = storage + energyTransaction
    if energy < 0: #selling energy
        print("Selling %d" % energy)
        storage=storage-energy
    elif energy > 0: #buying energy
        print("Buying %d" % energy)
        storage=storage+energy
    elif energy == 0:
        print("Nothing happened")

def coeffTransaction():
    if energyTransaction > 0:
        print("Decreasing price!")
        return -energyTransaction/1000000
    elif energyTransaction < 0:
        print("Inscreasing price!")
        return energyTransaction/1000000
    else:
        print("Nothing happened!")
        return 0

#def weather(): shared memory

def multi_threaded_client(connection):
    while True:
        data = int(client_socket.recv(1024))
        if not data:
            break
        handle_energy(data)
        energyTransaction = energyTransaction + data
        coeffTransaction()
        energyPrice = priceEnergy()
        energyTransaction=0
        print("Energy price %d" % energyPrice)
        value=input("Press y to send energy price to home(s) qnd continue this simulation\n")
        if value == 'y':    
             client_socket.sendall(energyPrice)
        else:
            print("Thanks for using this simulation")
    client_socket.close()

if __name__ == "__main__":
    threads = []
    #semaphore = Semaphore(5)
    #connect with homes with sockets 
    print("Starting market.")
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            client_socket, addr = server_socket.accept()
            print('Connected to: ' + addr[0] + ':' + str(addr[1]))
            start_new_thread(multi_threaded_client, (Client, ))
        server_socket.close()