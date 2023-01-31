import time
from multiprocessing import Pipe
import random


normal_temp = 23
loop_weather = 1
temp_interval = [-20, 40]
temp_interval_normal = [13, 27]
temp_interval


def update_weather(child_conn, temperature):
    while True:
        if temperature >= normal_temp:
            if temperature <= temp_interval_normal[1]:
                change = random.randint(-5, 5)
            else:
                change = random.randint(-5, 3)
        else:
            if temperature >= temp_interval_normal[0]:
                change = random.randint(-6, 6)
            else:
                change = random.randint(-6, 8)
        temperature += change

        if temperature <= temp_interval[0]:
            temperature = temperature + 8
        elif temperature >= temp_interval[1]:
            temperature = temperature - 6
        # print(temperature)
        message = child_conn.recv()
        if message.lower() == "get":
            child_conn.send(temperature)

        time.sleep(1)

