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
register = False

class NodoMemoria():

    def __init__(self):
        self.tamMax = 50008
        self.memoria = bytearray(self.tamMax)
        self.node_size = self.tamMax-8


        self.memoria[0] = 0x08
        for i in range(1,4):
            self.memoria[i] = 0x00


        tamMaxBytes = (self.tamMax-1).to_bytes(4,'little')

        for i in range(4,8):
            self.memoria[i] = tamMaxBytes[i-4]


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

        for k in range(4):
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
        #En [0] por que unpack desempaca como tupla

        posicionDatos = tamano_posicion[1]

        fechaCons_fechaCrea = struct.unpack("=ff", self.memoria[posicionDatos-7])

        metadatos.append(fechaCons_fechaCrea[0]) #Float de Fecha consulta

        metadatos.append(fechaCons_fechaCrea[1]) #Float de Fecha creacion

        return metadatos

    def guardar_pagina(self, tamano, id_pagina, datos):
        posicionMetadatos = self.leerUnDato(0,0)
        posicionDatos = self.leerUnDato(4,0)
        print(posicionDatos)

        metadatos = struct.pack("=Bii", id_pagina, tamano, posicionDatos)

        #Escribir la entrada de la pagina en metadatos
        contador = 0
        for i in range(posicionMetadatos, posicionMetadatos+9):
            self.memoria[i] = metadatos[contador]
            contador+=1

        fecha = time.time()

        encabezadoPag = struct.pack("=ff", fecha, fecha)

        #Escribir el encabezado de una pagina en datos(fechaConsulta/fechaCreacion)
        contador = 0
        for i in range(posicionDatos-7, posicionDatos+1):
            print(i)
            self.memoria[i] = encabezadoPag[contador]
            contador+= 1

        #Escribir los datos de una pagina
        contador = 0
        for i in range((posicionDatos-7)-tamano, posicionDatos-7):
            print(i)
            self.memoria[i] = datos[contador]
            contador += 1


        posicionMetadatos += 9
        posMetBytes = posicionMetadatos.to_bytes(4,'little')

        for i in range (0,4):
            self.memoria[i] = posMetBytes[i]

        posicionDatos -= (8+tamano)
        posDataBytes = posicionDatos.to_bytes(4,'little')

        for i in range (4,8):
            self.memoria[i] = posDataBytes[i-4]

        print("Pagina de tamano " , tamano ," guardada exitosamente")



    """
    Funcion que lee una pagina guardada en la memoria.
    Parametros:
        -id_pagina:la pagina que se requiere leer los metadatos.
    Retorna:
        el byteArray con los datos de la pagina
    """
    def leer_pagina(self, id_pagina):
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
            data[d] = self.memoria[posicionPagina-8-tamanoPagina+d]
        now = time.time()
        fecha = struct.pack("=f", now)
        for m in range(4):
            memoria[(posicionPagina-7)+m]=fecha[m]
        return data

    def leer_metadatos_paginas_guardadas(self):
        posicionMetadatos = self.leerUnDato(0,0)
        listaMetadatos = []
        for i in range(8, posicionMetadatos, 9):
            metadatos = leerMetadatos(i)
            listaMetadatos.append(metadatos)

        return listaMetadatos



class threadsInterface(threading.Thread):

    def __init__(self, name, nodoMemoria):

        threading.Thread.__init__(self)

        self.puerto_broad_ID = 5555
        self.puerto_tcp_ID = 3114
        self.hostID = "127.0.0.1"
        self.name = name
        self.kill = False
        self.nodoMem = nodoMemoria
        self.tamanoRestante = self.nodoMem.node_size
        #register = registration

    def run(self):
        global register
        my_name = self.name
        if(my_name == "registracionBroad"):
            paquete = manepack.paquete_broadcast_estoyAqui_NM_ID(5, self.nodoMem.node_size)
            nodoBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            nodoBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            nodoBroad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            nodoBroad.setblocking(0)

            nodoBroad.bind(('',self.puerto_broad_ID))

            while not register:

                nodoBroad.sendto(paquete, ('<broadcast>', self.puerto_broad_ID)) #intentar '10.1.255.255'
                print("Soy un nodo! Donde estan?")

                time.sleep(1)




        elif(my_name == "interfazListener"):
            #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as interListener:

            interListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #interListener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            interListener.bind((self.hostID, self.puerto_tcp_ID))

            while not self.kill:
                interListener.listen()
                conn, addr = interListener.accept()

                with conn:

                    data = conn.recv(691208)


                    if(data[0] == 0):
                        id_page, page_size, data = manepack.desempacar_paquete_guardar(data)
                        self.nodoMem.guardar_pagina(page_size, id_page, data)
                        self.tamanoRestante = self.tamanoRestante - page_size - 17
                        paquete = manepack.paquete_respuesta_guardar_ID_NM(2, id_page, self.tamanoRestante)
                        print(paquete)
                        conn.sendall(paquete)

                    elif(data[0] == 1):
                        id_pagina = manepack.desempacar_paquete_guardar(data)
                        pagina = self.nodoMem.leer_pagina(self, id_pagina)
                        paquete = self.nodoMem.paquete_respuesta_leer(3, id_pagina, pagina)
                        conn.sendall(paquete)

                    elif(data[0] == 2):
                        print("Se registro exitosamente.")
                        register = True

        elif(my_name == "tecladoListener"):

            print("Si desea ver el contenido actual del nodo de memoria presione la tecla N")
            while not self.kill:
                try:
                    if keyboard.is_pressed('n'):
                        print(" Mostrando contenido...")
                        time.sleep(0.5)
                        print()
                        listaMetadatos = self.nodoMem.leer_metadatos_paginas_guardadas()
                        print("ID Pagina\t\tTamano\t\tFecha Consulta\t\tFecha Creacion")
                        for i in listaMetadatos:
                            print("%d\t%d\t%s\t%s" %(i[0],i[1],time.ctime(i[2]),time.ctime(i[3])))
                            print()
                        print()
                except:
                    print("Ocurrio un error al imprimir los datos")


def threads_alive(Threads):
    for thread in Threads:
        if not thread.is_alive():
            return False
    return True


def main():

    threads = []
    memoryNode = NodoMemoria()
    register =  False

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

    while threads_alive(threads):

        try:

            [thread.join(1) for thread in threads
            if thread is not None and thread.is_alive()]

            if register:
                threadregister.kill=True

        except KeyboardInterrupt:

            print("Killing threads\n")
            for thread in threads:
                if(thread.kill == False):
                    thread.kill = True
            break
    #print("Main thread exited")


main()
