import os
import time
import sys
import threading
import struct
import datetime
import manejadorPaquetes as manepack

lock = threading.Lock()
first_time = True
registration = False

class NodoMemoria():

    def __init__(self):
        self.memoria = bytearray(50008)
        self.node_size = 50000


    """
    Funcion que un dato especifico de la memoria.
    Parametros:
        -posicion:donde empezar a leer desde el inicion de la memoria.
        -tamanoDato: El tamano de la parte de la memoria que hay que leer.
        -formato:el formato para convercion del dato
            formato = 0: 'I'
            formato = 1: 'i'
    """
    def leerUnDato(self,posicion,formato): #falta adoptar
        datoBytes = bytearray(4)
        for k in range (4):
            datoBytes[k] = self.memoria[posicion+k]

        datoReal = 0
        if(formato==0):
            datoReal = struct.unpack('I', datoBytes)
        elif(formato == 1):
            datoReal = struct.unpack('i', datoBytes)

        return datoReal[0]

    def leerMetadatos(self,id_pagina, posicion1):
        datoBytes1 = bytearray(8)
        datoBytes2 = bytearray(8)
        for k in range (8):
            datoBytes1[k] = self.memoria[posicion1+k]
        
        datoReal1 = struct.unpack('II', datoBytes)

        for f in range (8):
            datoBytes1[h] = self.memoria[datoReal1[1]+datoReal1[0]+h]
        
        datoReal2 = struct.unpack('ii', datoBytes)

        return datoReal1[0], datoReal1[1], datoReal2[0], datoReal2[1]


    def guardar_pagina():

    def leer_pagina():

    def leer_metadatos_paginas_guardadas():

    
class threadsInterface(threading.Thread):

    def __init__(self, name, nodoMemoria):

        threading.Thread.__init__(self)
        self.puerto_broad_ID = 5000
        self.puerto_tcp_ID = 3114
        self.hostID = "127.0.0.1"
        self.name = name
        self.kill = False
        self.nodoMem = nodoMemoria

    def run(self):

        my_name = self.name
        if(my_name == "registracionBroad")

            while(self.registration == false):
                paquete = manepack.paquete_broadcast_estoyAqui_NM_ID(5, self.node_size) 
                nodoBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                nodoBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                nodoBroad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                nodoBroad.bind(("", self.puerto_broad_ID))
                interBroad.sendto(paquete, ('<broadcast>', self.puerto_broad_ID))
            
            self.kill = True


        elif(my_name == "interfazListener"):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as interListener:

                interListener.bind((hostID, puerto_tcp_ID))

                while not self.kill:
                    memoryListener.listen()
                    conn, addr = memoryListener.accept()

                    with conn:

                        data = conn.recv(691208)

                        if(data[0] == 0):
                            {
                                
                            }

                        elif(data[0]== 1):
                            {

                            }

                        elif(data[0]== 2):
                            {
                                print("Se registro exitosamente.")
                                registration = True
                            }


        elif(my_name = "tecladoListener"):

            while not self.kill:




def main():

    threads = []

    threadregister = threadsInterface(name = "registracionBroad")
    threadinterfaz = threadsInterface(name = "interfazListener")
    threadteclado = threadsInterface(name = "tecladoListener")

    threadregister.start()
    threadinterfaz.start()
    threadteclado.start()

    treade.append(threadregister)
    threads.append(threadinterfaz)
    threads.append(threadteclado)

    while threads_alive(threads):

        try:

            [thread.join(1) for thread in threads
             if thread is not None and thread.is_alive()]

        except KeyboardInterrupt:

            print ("Killing threads\n")
            for thread in threads:
                if(thread.kill = False):
				    thread.kill = True

			break
    print ("Main thread exited")

main()