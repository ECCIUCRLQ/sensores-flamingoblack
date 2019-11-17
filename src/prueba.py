import manejadorPaquetes as manepack
import struct
import socket
import time
import sys
import uuid

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

if len(sys.argv) > 1:

    if sys.argv[1] == '0':

        cliente()

    elif sys.argv[1 == '1']:

        servidor()

else:

    op_code = 2
    id_page = 48
    size_page = 15
    data = "x" * 15
    #data_bytes = bytes(data, 'utf-8')
    data_bytes = bytearray([1,15,25,35,45])

    paqueteestoy = manepack.paquete_broadcast_estoyAqui_NM_ID(op_code, 15478)

    espacio_nodo = manepack.desempacar_paquete_estoyAqui(paqueteestoy)
    print (espacio_nodo)

    print ("The MAC address in formatted way is : ", end="") 
    print (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
    for ele in range(0,8*6,8)][::-1])) 

    mac_byte = uuid.getnode().to_bytes(6, 'little')

    paquete_quiero = manepack.paquete_broadcast_quieroSer_ID_ID(1, mac_byte, 4)
    mac_extraida, ronda = manepack.desempacar_paquete_quieroSer(paquete_quiero)

    print ("MAC obtenida : " + str(mac_extraida))
    print ("Ronda: " + str(ronda))



    '''

    paquete = manepack.paquete_respuesta_leer(op_code, id_page, data_bytes)

    print (paquete)
    print (paquete[0])
    print (paquete[1])

    for i in range(2, 7):

        print (paquete[i])

    '''