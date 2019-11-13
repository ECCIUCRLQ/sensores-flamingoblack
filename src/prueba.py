import manejadorPaquetes as manepack
import struct
import socket
import time
import sys

def cliente():

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 37020))

    while True:
    
        data, addr = client.recvfrom(1024)
        print ("Mensaje recibico del servidor: " + str(data))
        print ("Ip del servidor: " + str(addr))

        datos = data[6:(6+data[2])]
        print (datos)

def servidor():

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    server.settimeout(0.2)
    server.bind(("", 44444))

    oper = 0
    idp = 15
    size = 5
    data = bytearray([5,154,23,35,15])

    paquete = manepack.paquete_para_guardar(oper, idp, size, data)

    while True:
        server.sendto(paquete, ('<broadcast>', 37020))
        print ("Mensaje enviado!")
        time.sleep(1)

if sys.argv[1] == '0':

    cliente()

elif sys.argv[1 == '1']:

    servidor()