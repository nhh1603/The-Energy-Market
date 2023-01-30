import sysv_ipc
import socket
import multiprocessing
from home import Home

HOST = "localhost"
PORT = 1789

def handle_receive(mq):
    message, t = mq.receive()
    value = message.decode()
    print(value)

if __name__ == "__main__":
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.bind((HOST, PORT))
    #     s.listen()
    #     conn, addr = s.accept()
    #     with conn:
    #         print(f"Connected by {addr}")
    #         data = conn.recv(1024)
    #         print(data)
    #         print("Disconnecting from client: ", addr)

    key = 123
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    mq.remove()

    # message = str(1).encode()
    # mq.send(message, type = 3)
    # mq.send(message, type = 4)
    # mq.send("2", type = 3)
    # mq.send("2", type = 6)
    # mq.send("2", type = 5)

    # for i in range(5):
    #     message, t = mq.receive(type = -5)
    #     value = message.decode()
    #     print(value, t)


    # mq.remove()

    # home = Home(4000, 3000, 1)
    # home.exchange_market = 10
    # # home.update_rates(5000, 3000)
    # print(home.exchange_market)
