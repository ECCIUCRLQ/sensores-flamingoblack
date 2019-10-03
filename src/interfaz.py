# coding=utf-8
import os

def transform_into_key(byte_array):

    my_key = str(byte_array[0]) + str(byte_array[1]) + str(byte_array[2]) + str(byte_array[3])
    return my_key

def update_sensor(key):

    data = sensor_manager[key]
    if(data[0] == False):
        data[0] = True
        data[1] = 5
        # data[1] = metodo de MM que devuelve numero pagina
        data[2] = 0
        return
    else:
        if(data[3] == 5):
            if(data[2] == 500):
                # llamo a metodo para pedir nueva pagina
                # data[1] = actualizo nuevo numero de pagina
                data[2] = 5
                return
            else:
                data[2] += 5
        else:
            if(data[2] == 40000):
                # llamo a metodo para pedir nueva pagina
                # data[1] = actualizo nuevo numero de pagina
                data[2] = 8
                return
            else:
                data[2] += 8

def update_page_table(first_time):
    
    if(first_time):
        page_file = open("PageTableIndex.csv", "w+")

        for key in sensor_manager.keys():
            data = sensor_manager[key]
            page_file.write(key + "," + str(data[1]) + "\n")

        page_file.close()
    else:
        page_file = open("PageTableIndex.csv", "r+")
        store_buffer = []
        line = page_file.readline()
        
        while line:
            store_buffer.append(line.strip("\n"))
            line = page_file.readline()
        
        page_file.close()
        os.remove("PageTableIndex.csv")

        new_page_file = open("PageTableIndex.csv", "w+")

        for key in sensor_manager.keys():
            data = sensor_manager[key]
            new_page_file.write(store_buffer.pop() + "," + str(data[1]) + "\n")

        new_page_file.close()

sensor_manager = {
    # key: [primera vez, página actual, por donde va en la página, tamaño del dato del sensor]
    "1001": [False, -1, -1, 5],
    "1002": [False, -1, -1, 5],
    "2001": [False, -1, -1, 5],
    "2002": [False, -1, -1, 5],
    "3001": [False, -1, -1, 5],
    "3002": [False, -1, -1, 5],
    "4001": [False, -1, -1, 5],
    "4002": [False, -1, -1, 5],
    "5001": [False, -1, -1, 5],
    "5002": [False, -1, -1, 8],
    "6001": [False, -1, -1, 8],
    "6002": [False, -1, -1, 8]
}

miArreglo = bytearray([4,0,0,1])
new_key = transform_into_key(miArreglo)
update_sensor(new_key)
update_page_table(0)

'''

for key in sensor_manager.keys():
    print key

for i in sensor_manager:
    if(i == new_key):
        print ("Got key")

'''