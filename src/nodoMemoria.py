import os
import time
import sys
import threading
import struct
import manejadorPaquetes as manepack

lock = threading.Lock()
first_time = True

class NodoMemoria():

    def __init__(self):
        self.memoria = bytearray(50008)
        self.puerto_broad_ID = 5000
        self.puerto_tcp_ID = 3114
        self.hostID = "127.0.0.1"
        self.socketID = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.node_size = 50000

        registration = False

        while(registration == false):
            paquete = manepack.paquete_broadcast_estoyAqui_NM_ID(op_code, self.node_size) #agregar el op.code


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