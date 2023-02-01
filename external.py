#external, child de market, sends signals random events
from multiprocessing import Process
import os
import sys
import time
import signal
import random

def handle_external():
    os.kill(int(os.getppid()), signal.SIGUSR1)
