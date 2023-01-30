from multiprocessing import Process, Semaphore
import random
import time
import sys
import sysv_ipc
import decimal
import threading
import socket


HOST = "localhost"
PORT = 1789
storage = 1000000 #W
energyTransaction = 0
energyPrice = 0.145 #e/KWh

#functions

def priceEnergy():
	coeffAtte = 0.99
	#coeffWeather = weather()
	coeffTrans = coeffTransaction()
	energyPrice = coeffAtte * energyPrice + coeffTrans * energyPrice
	return energyPrice

def handle_energy(energy):
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

if __name__ == "__main__":
    threads = []
    semaphore = Semaphore(5)
    #connect with homes with sockets 
    print("Starting market.")
    with semaphore:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            client_socket, addr = server_socket.accept()
        with client_socket:
                print(f"Connected by {addr}")
        while True:
            data = client_socket.recv(1024)
            handle_energy(data)
            energyTransaction = energyTransaction + data
            client_socket.close()
            coeffTransaction()
            energyPrice = priceEnergy()
            energyTransaction=0
            print("Energy price %d" % energyPrice)
            value=input("Press y to send energy price to home(s) qnd continue this simulation\n")
            if value == 'y':    
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    s.sendall(energyPrice)
            else:
                print("Thanks for using this simulation")
                break