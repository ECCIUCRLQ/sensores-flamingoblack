import os

class AdministradorMem:

    def __init__(self):
        self.memoriaPrincipal = [bytearray(200000),bytearray(2500)]

        self.contadorPaginas = 0
        self.tablaPaginas = []
        self.colaPaginas = [[],[]]

    def pagEstaEnPrincipal(self,numPagina):
        esta = True
        if ( self.tablaPaginas[numPagina]==-1):
            esta = False

        return esta

    def getMemPrinLlena(self, tamano):
        llena = False
        if (len(self.colaPaginas[tamano]) == 5):
            llena = True

        return llena

    def getPaginaPorCambiar(self, tamano):
        return self.colaPaginas[tamano].pop()

    
    def vaciarPagina(self,tamano,posicion):
        longitud = 0
        if (tamano == 0):
            longitud = 40000
        else:
            longitud == 500

        for i in range (posicion,posicion+longitud):
            self.memoriaPrincipal[tamano][i] == 0x00

    def enviarPagMemSecundaria(self, tamano, numPagina):
        busDatos = bytearray(1)
        if (tamano == 0):
            busDatos = bytearray(40000)
        else:
            busDatos = bytearray(500)

        posicion = self.tablaPaginas[numPagina]
        for i in range(len(busDatos)):
            busDatos[i] = self.memoriaPrincipal[tamano][posicion+i]

        archivo = open("paginas/" + str(numPagina) + ".txt","w+b")

        archivo.write(busDatos)
        
        self.vaciarPagina(tamano,posicion)
        self.tablaPaginas[numPagina] = -1

    def cargarPagMemSecundaria(self,tamano,numPagina,posicion):
        nombreArchivo = "paginas/" + str(numPagina) + ".txt"
        archivo = open(nombreArchivo, "rb")
        busDatos = bytearray(archivo.read())
        os.remove(nombreArchivo)

        longitud = 0
        if (tamano == 0):
            longitud = 40000
        else:
            longitud = 500

        for i in range(posicion,posicion+longitud):
            self.memoriaPrincipal[tamano][i] = busDatos[i-posicion]
            
        self.tablaPaginas[numPagina] = posicion

    def buscarPosicionVacia(self,tamano):
        posicion = 0
        incremento = 0
        if tamano == 0:
            incremento = 40000
        else:
            incremento = 500

        encontrada = False
        while not encontrada:
            if posicion in self.tablaPaginas:
                posicion += incremento
            else:
                encontrada = True

        return posicion

    def swapPaginas(self,tamano,pagNueva):
        pagVieja = self.getPaginaPorCambiar(tamano)
        posicion = self.tablaPaginas[pagVieja]
        self.enviarPagMemSecundaria(tamano,pagVieja)

        self.cargarPagMemSecundaria(tamano,pagNueva,posicion)
        self.colaPaginas[tamano].insert(0,pagNueva)

        return posicion

    """
    Funciones a utilizar en interfaz
    """
    
    def guardarDato(self,tamano,numPagina,offset,dato):
        posicion = -1
        if (self.pagEstaEnPrincipal(numPagina)):
            posicion = self.tablaPaginas[numPagina]
        else:
            posicion = self.swapPaginas(tamano,numPagina)

        desplaz = 0
        if tamano == 0:
            desplaz = 8
        else:
            desplaz = 5

        posicion += offset
        for i in range (posicion,posicion+desplaz):
            self.memoriaPrincipal[tamano][i] = dato[i-posicion]


    def reservarPagina(self,tamano):
        posicion = 0
        if self.getMemPrinLlena(tamano):
            paginaCambiar = self.getPaginaPorCambiar(tamano)
            posicion = self.tablaPaginas[paginaCambiar]
            self.tablaPaginas[paginaCambiar] = -1
            self.enviarPagMemSecundaria(tamano,paginaCambiar)
        else:
            posicion = self.buscarPosicionVacia(tamano)

        self.tablaPaginas.append(posicion)
        self.colaPaginas[tamano].insert(0,self.contadorPaginas)
        pagAsignada = self.contadorPaginas
        self.contadorPaginas+=1

        print(self.tablaPaginas)
        print(self.colaPaginas)
        print("-----------")

        return pagAsignada

    def obtenerDatos(self,tamano,listaPaginas):
        tamanoPagina = 0
        if (tamano == 0):
            tamanoPagina = 40000
        else:
            tamanoPagina = 500

        tamanoBus = tamanoPagina*len(listaPaginas)

        busDatos = bytearray(tamanoBus)

        contadorBus = 0
        for i in range (len(listaPaginas)):
            if self.pagEstaEnPrincipal(listaPaginas[i]):
                posicion = self.tablaPaginas[listaPaginas[i]]
            else:
                posicion = self.swapPaginas(tamano,listaPaginas[i])

            for j in range (posicion,posicion+tamanoPagina):
                busDatos[contadorBus] = self.memoriaPrincipal[tamano][j]
                contadorBus+=1

        return busDatos

    def printMemPrin(self):
        print(self.memoriaPrincipal[1])



"""
admin = AdministradorMem()
admin.reservarPagina(1)
admin.reservarPagina(0)
admin.reservarPagina(1)
admin.reservarPagina(0)
admin.reservarPagina(0)
admin.reservarPagina(1)
admin.reservarPagina(1)
admin.reservarPagina(1)
admin.reservarPagina(1)
dato = bytearray([0x01,0x02,0x03,0x04,0x05])
admin.guardarDato(1,0,0,dato)
admin.printMemPrin()
"""
