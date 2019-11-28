import os
import time
import sys
import threading
import struct
import datetime
import manejadorPaquetes as manepack
import keyboard

lock = threading.Lock()
first_time = True
registration = False

class NodoMemoria():

    def __init__(self):
        self.memoria = bytearray(50008)
        self.node_size = 50000


    """
    Funcion que lee un dato especifico de la memoria.
    Parametros:
        -posicion:donde empezar a leer desde el inicion de la memoria.
        -tamanoDato: El tamano de la parte de la memoria que hay que leer.
        -formato:el formato para convercion del dato
            formato = 0: 'I'
            formato = 1: 'i'
    """
    def leerUnDato(self,posicion,formato): 
        datoBytes = bytearray(4)
        for k in range (posicion, posicion+4):
            datoBytes[k] = self.memoria[posicion+k]

        datoReal = 0
        if(formato==0):
            datoReal = struct.unpack('I', datoBytes)
        elif(formato == 1):
            datoReal = struct.unpack('i', datoBytes)

        return datoReal[0]

    """
    Funcion que lee los metadatos de una pagina guardada en la memoria.
    Parametros:
        -id_pagina:la pagina que se requiere leer los metadatos.
        -posicion: posicion de esta pagina en la memoria.
    """
    def leerMetadatos(self,id_pagina, posicion):
        datoBytes1 = bytearray(8)
        datoBytes2 = bytearray(8)
        for k in range (posicion, posicion+8):
            datoBytes1[k] = self.memoria[posicion+k]
        
        datoReal1 = struct.unpack('II', datoBytes1)

        for f in range (datoReal1[1],datoReal1[0]+8):
            datoBytes2[f] = self.memoria[datoReal1[1]+datoReal1[0]+f]
        
        datoReal2 = struct.unpack('ii', datoBytes2)

        return datoReal1[0], datoReal1[1], datoReal2[0], datoReal2[1]


    #def guardar_pagina(self, tamano, id_pagina, datos):


    def leer_pagina(self, id_pagina):
        bytesTemp = bytearray(4)
        tamanoPagina = 0
        posicionPagina = 0
        offsetMeta = 0
        for i in range (0, 4):
            bytesTemp[i] = self.memoria[i]
        offsetMeta = struct.unpack('I', offsetMetaBytes)

       # for j in range(8, offsetMeta, j+12):
        #    for k in range(j,j+4):



    def leer_metadatos_paginas_guardadas(self):
        lista = "hola"
        return lista
    
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
        if(my_name == "registracionBroad"):

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
                                #print("Se registro exitosamente.")
                                #registration = True
                            }


        elif(my_name == "tecladoListener"):

            while not self.kill:
              if keyboard.is_pressed('n'):
                listaMetadatosPorPagina = self.nodoMem.leer_metadatos_paginas_guardadas()
                print(listaMetadatosPorPagina)
                break
                




def main():

    threads = []
    memoryNode = NodoMemoria()

    threadregister = threadsInterface(name = "registracionBroad", nodoMemoria =  memoryNode)
    threadinterfaz = threadsInterface(name = "interfazListener", nodoMemoria = memoryNode)
    threadteclado = threadsInterface(name = "tecladoListener", nodoMemoria = memoryNode)

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
                if(thread.kill == False):
                    thread.kill = True
            break
    print ("Main thread exited")

main()

#memoria[50008]

#22 500 6

#memoria[0-3] = offset = 8 => 8+12
#memoria[4-7] = offset2 = 50 007
#memoria[8-11] = 22
#memoria[12-15] = 500
#memoria[16-19] = 6

#memoria[50007-4] = fecha1
#memoria[50007 -8] = fecha2
#memoria[50007-8-500] = datos = reemplasa el offset2
