import os
import time
import sys
import threading
import struct
import manejadorPaquetes as manepack

lock = threading.Lock()
first_time = True

class threadsInterface(threading.Thread):

    def __init__(self, name):

        threading.Thread.__init__(self)
        self.name = name
        self.kill = False

    def run(self):

        my_name = self.name
        if(my_name == "interfaz"):

            while not self.kill:
                
                if(first_time):

                else:
                    



        elif(my_name = "teclado"):

            while not self.kill:




def main():

    threads = []

    threadinterfaz = threadsInterface(name = "interfaz")
    threadteclado = threadsInterface(name = "teclado")

    threadinterfaz.start()
    threadteclado.start()

    threads.append(threadinterfaz)
    threads.append(threadteclado)

    while threads_alive(threads):

        try:

            [thread.join(1) for thread in threads
             if thread is not None and thread.is_alive()]

        except KeyboardInterrupt:

            print ("Killing threads\n")
            threadinterfaz.kill = True
            threadteclado.kill = True