import sysv_ipc
import socket
import multiprocessing
import random
import time
from home import Home
from multiprocessing import Process, Value, Lock, Pipe
from weather import update_weather
import weather

temperature = 23

if __name__ == "__main__":

    parent_conn, child_conn = Pipe()
    p = Process(target = update_weather, args = (child_conn, temperature))
    p.start()
    phrase = input("Send command: ")
    # parent_conn.send("Get")
    while phrase.lower() != "end":
        parent_conn.send(phrase)
        temperature = parent_conn.recv()
        print(temperature)
        phrase = input("Send: ")

    parent_conn.close()
    child_conn.close()
    p.terminate()
    p.join()


