import manejadorPaquetes as manepack
import struct
import socket
import time
import sys
import uuid

page_manager = {
    1:5,
    2:4,
    3:8
}

node_manager = {
    5:[1459, 500],
    1:[25800, 4500]
}

page_manager2 = {

}

node_manager2 = {
    1:[25800, 5000],
    5:[1459, 500]
}

nodeCounter = 2
pageCounter = 0

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

def create_dump():

    dump1 = bytearray()
    dump2 = bytearray()

    for page in page_manager:

        dump1.append(page)
        dump1.append(page_manager[page])

    for node in node_manager:

        dump2.append(node)
        data = node_manager[node]
        
        ip_node = struct.pack("I", data[0])
        size_node = struct.pack("I", data[1])
    
        for i in range(4):

            dump2.append(ip_node[i])

        for i in range(4):

            dump2.append(size_node[i])

    return dump1, dump2

def read_dump(data):

    global page_manager2
    global node_manager2

    page_amount = data[0]
    page_dump = data[2]

    page_iterator = 0

    while page_amount > 0:

        page_manager2[page_dump[page_iterator]] = page_dump[page_iterator+1]
        page_iterator += 2
        page_amount -= 1

        node_amount = data[1]
        node_dump = data[3]

    node_iterator = 0

    while node_amount > 0:

        ip = struct.unpack("I", node_dump[node_iterator+1:(node_iterator+1)+4])
        size = struct.unpack("I", node_dump[(node_iterator+1)+4:((node_iterator+1)+4)+4])

        value = [ip[0], size[0]]
        node_manager2[node_dump[node_iterator]] = value
        node_iterator += 9
        node_amount -= 1

if len(sys.argv) > 1:

    if sys.argv[1] == '0':

        cliente()

    elif sys.argv[1 == '1']:

        servidor()

else:

    op_code = 2
    id_page = 48
    size_page = 11
    data_bytes = bytearray([1,15,25,35,45,148,250,15,17,24,21])

    # paquete y desempaque estoy aqui

    paqueteestoy = manepack.paquete_broadcast_estoyAqui_NM_ID(op_code, 15478)
    espacio_nodo = manepack.desempacar_paquete_estoyAqui(paqueteestoy)

    # paquete y desempaque quier ser

    mac_byte = uuid.getnode().to_bytes(6, 'little')

    paquete_quiero = manepack.paquete_broadcast_quieroSer_ID_ID(1, mac_byte, 4)
    mac_extraida, ronda = manepack.desempacar_paquete_quieroSer(paquete_quiero)

    # paquete y desempaque soyactivo

    datos = []
    dump1 = bytearray([1,8,0x10,3,2,4])
    dump2 = bytearray([1,3,2,6,5,7,8,0x10,4])
    paquetesoy = manepack.paquete_broadcast_soyActivo_ID_ID(op_code, 3, 1, dump1, dump2)
    datos = manepack.desempacar_paquete_soyActivo(paquetesoy)
    print (datos)

    # paquete y desempaque keepalive con y sin cambios

    paqueteKA = manepack.paquete_broadcast_keepAlive_ID_ID(op_code, 3, 1, dump1, dump2)
    datos2 = manepack.desempacar_paquete_keepAlive(paqueteKA)
    print (datos2)

    paqueteKA = manepack.paquete_broadcast_keepAlive_ID_ID(op_code, 0, 0, 0, 0)
    datos2 = manepack.desempacar_paquete_keepAlive(paqueteKA)
    print (datos2)

    # paquete y desempaque respuesta leer 

    paqueteresleer = manepack.paquete_respuesta_leer(op_code, id_page, dump1)
    datos3 = manepack.desempacar_paquete_respuesta_leer(paqueteresleer, id_page, 6)
    print (datos3)

    # paquete y desempaque respuesta guardar ID_NM

    paqueteResGuaID_NM = manepack.paquete_respuesta_guardar_ID_NM(op_code, id_page, 1454)
    datos4 = manepack.desempacar_paquete_guardar_respuesta_ID_NM(paqueteResGuaID_NM, id_page)

    # paquete y desempaque respuesta guardar ML_ID

    paqueteResGuaML_ID = manepack.paquete_respuesta_guardar_ML_ID(op_code, id_page)
    datos5 = manepack.desempacar_paquete_guardar_respuesta_ML_ID(paqueteResGuaML_ID, id_page)

    # paquete para guardar, tanto en ID como NM

    paqueteGua = manepack.paquete_para_guardar(op_code, id_page, 6, dump1)
    print (paqueteGua)

    # paquete para leer, tanto en ID como NM

    paqueteLee = manepack.paquete_para_leer(op_code, id_page)
    print (paqueteLee)

    dump1, dump2 = create_dump()
    paqueteSoyActivo = manepack.paquete_broadcast_soyActivo_ID_ID(2, 3, 2, dump1, dump2)

    datos6 = manepack.desempacar_paquete_keepAlive(paqueteSoyActivo)
    print (datos6)

    read_dump(datos6)
    print (page_manager)
    print (page_manager2)
    print (node_manager)
    print (node_manager2)