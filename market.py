from multiprocessing import Process
import random
import time
import sys
import sysv_ipc
import decimal
import threading
import socket


HOST = "localhost"
PORT = 1789

energyPrice = 0.145
nbSell = 0
nbBuy = 0  	 

#functions

def sellEnergy(energy):
	print("Selling %d" % energy)
	energyInitial = energyInitial - energy
	nbSell = nbSell + 1

def buyEnergy(energy):
	print("Buying %d" % energy)
	energyInitial = energyInitial + energy
	nbBuy = nbBuy + 1

def priceEnergy():
	coeffAtte = 0.99
	#coeffWeather = weather()
	coeffTrans = limTransaction()
	energyPrice = coeffAtte * energyPrice + coeffTrans * 0.01
	return energyPrice
		
def limTransaction():
	coeff = random.random()
	if nbBuy > 5:
		print("Too much of buying, inscreasing price...")
		return coeff
	elif nbSell > 5:
		print("Too much of selling, lowering price...")
		return -coeff
	else:
		return 0

#def weather(): # shared memory

if __name__ == "__main__":
 threads = []
# connect with homes with sockets 
 print("Starting market.")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    client_socket, addr = server_socket.accept()
    with client_socket:
        print(f"Connected by {addr}")
        while True:
            data = client_socket.recv(1024)
            if data == 1:
                p = threading.Thread(target=sellEnergy, args= (data))
                p.start()
                threads.append(p)
                nbSell=+1
            if data == 2:
                q = threading.Thread(target=buyEnergy, args= (data))
                q.start()
                threads.append(q)
                nbBuy=+1
            if data == 3:
                print("Terminating market.")
                for thread in threads:
                    thread.join()
                client_socket.close()
                break
    limTransaction()
    energyPrice = priceEnergy()
    print("Energy price %d" % energyPrice)
    time.sleep(5)
