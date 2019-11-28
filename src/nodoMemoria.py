import os
import time
import sys
import threading
import struct
import datetime
import manejadorPaquetes as manepack
import keyboard
import socket

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

    def leerUnDato(self, posicion, formato):
        datoBytes = bytearray(4)
        for k in range(posicion, posicion+4):
            datoBytes[k] = self.memoria[posicion+k]

        datoReal = 0
        if(formato == 0):
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

    def leerMetadatos(self, posicion):

        metadatos = []

        metadatos.append(self.memoria[posicion]) #Byte de ID de pagina

        tamano_posicion = struct.unpack("=II", self.memoria[posicion+1])

        metadatos.append(tamano_posicion[0])   #Entero de tamano de pagina
        #En [0] por que unpack desempaca com tupla

        posicionDatos = tamano_posicion[1]

        fechaCons_fechaCrea = struct.unpack("=ff", self.memoria[posicionDatos-7])

        metadatos.append(fechaCons_fechaCrea[0]) #Float de Fecha consulta

        metadatos.append(fechaCons_fechaCrea[1]) #Float de Fecha creacion

        return metadatos

    def guardar_pagina(self, tamano, id_pagina, datos):
        posicionMetadatos = self.leerUnDato(0,0)
        posicionDatos = self.leerUnDato(4,0)

        metadatos = struct.pack("=Bii", id_pagina, tamano, posicionDatos)

        #Escribir la entrada de la pagina en metadatos
        for i in range(posicionMetadatos, posicionMetadatos+9):
            self.memoria[i] = metadatos[i-posicionMetadatos]

        fecha = time.time()

        encabezadoPag = struct.pack("=ff", fecha, fecha)

        #Escribir el encabezado de una pagina en datos(fechaConsulta/fechaCreacion)
        contador = 0
        for i in range(posicionDatos-7, posicionDatos+1):
            self.memoria[i] = encabezadoPag[contador]
            contador+= 1

        #Escribir los datos de una pagina
        contador = 0
        for i in range((posicionDatos-7)-tamano, posicionDatos-7):
            self.memoria[i] = datos[contador]
            contador += 1

        print("Pagina de tamano " , tamano ," guardada exitosamente")



    """
    Funcion que lee una pagina guardada en la memoria.
    Parametros:
        -id_pagina:la pagina que se requiere leer los metadatos.
    Retorna:
        el byteArray con los datos de la pagina
    """
    def leer_pagina(self, id_pagina): #No terminado
        offsetMeta = self.leerUnDato(0,0)
        bytesTemp2 = bytearray(8)
        tamanoPagina = 0
        posicionPagina = 0

        for j in range(8, offsetMeta, 9):
            if self.memoria[j] == id_pagina:
                for n in range (8):
                    bytesTemp2[n] = self.memoria[j+1+n]
                    metaTemp = struct.unpack('II', bytesTemp)
                    tamanoPagina = metaTemp[0]
                    posicionPagina = metaTemp[1]

                break
        data = bytearray(tamanoPagina)
        for d in range(tamanoPagina):
            data[d] = self.memoria[offsetMeta-8-tamanoPagina+d]

        return data

    def leer_metadatos_paginas_guardadas():
        posicionMetadatos = self.leerUnDato(0,0)
        listaMetadatos = []
        for i in range(8, posicionMetadatos, 9):
            metadatos = leerMetadatos(i)
            listaMetadatos.append(metadatos)

      return listaMetadatos

    def threads_alive(self, Threads):
        for thread in Threads:
            if not thread.is_alive():
                return False
        return True


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

            while(registration == False):
                paquete = manepack.paquete_broadcast_estoyAqui_NM_ID(
                    5, self.nodoMem.node_size)
                nodoBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                nodoBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                nodoBroad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                nodoBroad.bind(("", self.puerto_broad_ID))
                nodoBroad.sendto(paquete, ('<broadcast>', self.puerto_broad_ID))

            self.kill = True

        elif(my_name == "interfazListener"):
            #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as interListener:

            interListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            interListener.bind((self.hostID, self.puerto_tcp_ID))

            while not self.kill:
                interListener.listen()
                conn, addr = interListener.accept()

                with conn:

                    data = conn.recv(691208)

                    if(data[0] == 0):
                        {

                        }

                    elif(data[0] == 1):
                        {

                        }

                    elif(data[0] == 2):
                        {
                                #print("Se registro exitosamente.")
                                #registration = True
                        }

        elif(my_name == "tecladoListener"):

            print("Si desea ver el contenido actual del nodo de memoria presione la tecla N")
            while not self.kill:
                if keyboard.is_pressed('n'):
                    listaMetadatosPorPagina = nodoMem.leer_metadatos_paginas_guardadas()
                    print("ID Pagina\tTamano\tFecha Ultima Consulta\tFecha Creacion")


def main():

    threads = []
    memoryNode = NodoMemoria()

    threadregister = threadsInterface(
        name="registracionBroad", nodoMemoria=memoryNode)
    threadinterfaz = threadsInterface(
        name="interfazListener", nodoMemoria=memoryNode)
    threadteclado = threadsInterface(
        name="tecladoListener", nodoMemoria=memoryNode)

    threadregister.start()
    threadinterfaz.start()
    threadteclado.start()

    threads.append(threadregister)
    threads.append(threadinterfaz)
    threads.append(threadteclado)

    while memoryNode.threads_alive(threads):

        try:

            [thread.join(1) for thread in threads
             if thread is not None and thread.is_alive()]

        except KeyboardInterrupt:

            print("Killing threads\n")
            for thread in threads:
                if(thread.kill == False):
                    thread.kill = True
            break
    print("Main thread exited")


main()

# memoria[50008]

# 22 500 6

# memoria[0-3] = offset = 8 => 8+12
# memoria[4-7] = offset2 = 50 007
#memoria[8-11] = 22
#memoria[12-15] = 500
#memoria[16-19] = 6

#memoria[50007-4] = fecha1
#memoria[50007 -8] = fecha2
# memoria[50007-8-500] = datos = reemplasa el offset2
