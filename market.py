from multiprocessing import Process, Semaphore
import random
import time
import sys
import sysv_ipc
import decimal
from threading import Thread
import socket
from _thread import *
from socketserver import ThreadingMixIn 

HOST = "localhost"
PORT = 1789
storage = 1000000
energyTransaction = 0
energyPrice = 0.145 #e/KWh
loop0 = True
loop1 =False

# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread):
    def __init__(self,ip,port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port
        print("[+] New server socket thread started for " + ip + ":" + str(port))
    def run(self):
        global loop0
        global energyTransaction
        global energyPrice
        while True : 
            data = conn.recv(1024).decode('utf8')
            print(data)
            if not data:
                #print("Bye")
                break
            if data == 'end':
                print("End of transactions")
                loop0 = False
                break
            else:
                data = int(data)
                handle_energy(data)
                energyTransaction = energyTransaction + data
                coeffTransaction()
                energyPrice = priceEnergy()
                energyTransaction = 0
                print("Energy price %f\n" % energyPrice) 

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

    
if __name__ == "__main__":
    threads = []

    #connect with homes with sockets 
    print("Starting market.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))

    while loop0:
        server_socket.listen(5)
        (conn, (ip,port)) = server_socket.accept()
        newthread = ClientThread(ip,port)
        newthread.start()
        threads.append(newthread)
        for t in threads:
            t.join()
        loop1 = True
    
    while loop1:
        print(energyPrice)
        value=input("Press y to send energy price to home(s) and continue this simulation\n")
        if value == 'y':
            print("Sending...")    
            conn.sendall(str(energyPrice).encode())
        else:
            print("Thanks for using this simulation")
    