
import os
import sys
import time
import threading
from multiprocessing import Process, Value, Lock
import random
import multiprocessing
import time

def weather(temperature):
    temperature.value=23
    min = -20
    max = 40
    while True:
        print(temperature.value)
        a=random.random()
        if a > 0.5:
            temperature.value=temperature.value+1
        else:
            temperature.value=temperature.value-1
        
        if temperature.value > 27:
            print("It's getting hot! Price inscreasing...")
            return a
        elif temperature.value < 13:
            print("It's getting cold! Price increasing...")
            return -a
        else:
            print("Normal temperature! Nothing happens")

        if temperature.value == min:
            temperature.value=temperature.value+5
        elif temperature.value == max:
            temperature.value=temperature.value-5
        time.sleep(1)

if __name__=="__main__":
    temp = multiprocessing.Value('i', 23)

    w = Process(target=weather, args=(temp,))
    w.start()
    w.join()

    print(temp.value)
