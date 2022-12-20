"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import graph as gr
import sys
import threading
import controller
from tabulate import tabulate
import folium
from DISClib.ADT import list as lt
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printCargaDeDatos(analyzer, sizeEE, sizeT, sizeA, lonslats):
    stops = analyzer["stops"]
    grafo = analyzer["grafo"]
    rutas = analyzer["rutas"]
    lonMin, lonMax, latMin, LatMax = lonslats
    headers = ["identificador", "coordenadas (lat, lon)", "número de vértices adyacentes"]
    datos = []
    print("La cantidad de estaciones exclusivas es de: "+str(sizeEE))
    print("La cantidad de estaciones con transbordos es de: "+str(sizeT))
    print("La cantidad de rutas registradas es de: "+str(sizeA)+" o, "+str(lt.size(rutas)))
    print("El rango del área rectangular de Barcelona que cubre la red de buses es de...\nlongitud mínima: "+str(lonMin)+", longitud máxima: "+str(lonMax)+", latitud mínima: "+str(latMin)+", latitud máxima: "+str(LatMax))
    print("la cantidad de vértices es de: " + str(gr.numVertices(grafo)))
    print("\nLos primeros 5 y últimos 5 vértices agregados al grafo....")
    vertices = gr.vertices(grafo)
    for i in range(1,6):
        llave = lt.getElement(vertices, i)
        entry = mp.get(stops, llave)
        adjacencias = lt.size(gr.adjacents(grafo, llave))
        if entry is not None:
            valor = me.getValue(entry)
            lat = valor["Latitude"]
            lon = valor["Longitude"]
            coordenada = (lat, lon)
        else:
            coordenada = "transbordo"
        datos.append([llave, coordenada, adjacencias])
    for j in range(lt.size(vertices)-3, lt.size(vertices)+1):
        llave = lt.getElement(vertices, j)
        entry = mp.get(stops, llave)
        adjacencias = lt.size(gr.adjacents(grafo, llave))
        if entry is not None:
            valor = me.getValue(entry)
            lat = valor["Latitude"]
            lon = valor["Longitude"]
            coordenada = (lat, lon)
        else:
            coordenada = "transbordo"
        datos.append([llave, coordenada, adjacencias])
    print(tabulate(datos, headers, "grid"))

def printReq1(distancia, cant_es, cant_trans, est):
    headers = ["identificadorA", "identificadorB", "distancia entre A y B"]
    datos = []
    print("La distancia total del recorrido es de: "+str(distancia)+" km")
    print("La cantidad de estaciones es de: " + str(cant_es))
    print("La cantidad de transbordos es de: " + str(cant_trans))
    for camino in lt.iterator(est):
        vertexA = camino["vertexA"]
        vertexB = camino["vertexB"]
        dist = camino["weight"]
        datos.append([vertexA, vertexB, dist])
    print(tabulate(datos, headers, tablefmt="grid"))

def printReq2(distancia, retorno, estaciones, contador_transbordos):
    sizeEstacionesBajables = lt.size(estaciones)
    sizeEstacionesTotales = lt.size(retorno)
    headers_estaciones_totales = ["identificador1" , "identificador2", "distancia"]
    datos_estaciones_totales = []
    headers_estaciones_bajables = ["estaciones y buses en donde debes bajarte"]
    datos_estaciones_bajables = []
    print("La distancia total es de: " +str(distancia))
    print("La cantidad de transbordos es de: " +str(contador_transbordos))
    print("La cantidad de estaciones en las que debes bajarte es de: " + str(sizeEstacionesBajables))
    print("La cantidad de estaciones totales es de: " + str(sizeEstacionesTotales))
    for tupla in lt.iterator(retorno):
        estacion1, estacion2, dist = tupla
        datos_estaciones_totales.append([estacion1, estacion2, dist])
    for est in lt.iterator(estaciones):
        datos_estaciones_bajables.append([est])
    print(tabulate(datos_estaciones_totales, headers_estaciones_totales, "grid"))
    print(tabulate(datos_estaciones_bajables, headers_estaciones_bajables, "grid"))

def printReq3(oficial, size):
    headers = ["cantidad de estaciones", "primeras 3 estaciones", "últimas 3 estaciones"]
    primeras = []
    ultimas = []
    datos = []
    print("La cantidad de componentes conectados es de: " + str(size))
    for llave in lt.iterator(mp.keySet(oficial)):
        entry = mp.get(oficial, llave)
        valor = me.getValue(entry)
        for i in range(1,4):
            element = lt.getElement(valor, i)
            primeras.append(element)
        for j in range(lt.size(valor)-3,lt.size(valor)):
            element = lt.getElement(valor, j)
            ultimas.append(element)
        datos.append([llave, primeras, ultimas])
        primeras = []
        ultimas = []
    print("La información de los 5 componentes conectados más grandes es de: ")
    print(tabulate(datos, headers, "grid"))

def printReq4(path, estacionI, estacionF, distI, distF, distancia, estaciones, transbordos):
    headers = ["identificadorA", "identificadorB", "distancia entre A y B"]
    datos = []
    print("-------------")
    print("La estacion más cercana a la localización inicial es: " + str(estacionI))
    print("La estación más cercana a la localización final es: " + str(estacionF))
    print("La distancia desde la localización inicial a la estación más cercana es de: " + str(distI))
    print("La distancia desde el punto final a la estación más cercana es de: " + str(distF))
    print("La distancia total desde la estación de inicio " +str(estacionI) + " hasta la estación final " + str(estacionF) + " es de: " + str(distancia))
    print("La cantidad de transbordos es de: " + str(transbordos))
    print("La cantidad de estaciones es de: " + str(estaciones))
    print("-------------")
    for camino in lt.iterator(path):
        vertexA = camino["vertexA"]
        vertexB = camino["vertexB"]
        dist = camino["weight"]
        datos.append([vertexA, vertexB, dist])
    print(tabulate(datos, headers, tablefmt="grid"))

def printReq5(paqueteReq5, estI):
    estaciones, size, distancias = paqueteReq5
    headers = ["identificador", "coordenadas (lat, lon)", "distancia de la estación inicial"]
    datos = []
    print("La cantidad de estaciones alcanzables desde la estación con el identificador " + str(estI) + " es de: " + str(size))
    for tupla in lt.iterator(distancias):
        est, dist, coord = tupla
        datos.append([est, coord, dist])
    print(tabulate(datos, headers, "grid"))
    
def printReq6(paqueteReq6):
    path, distancias, contadores = paqueteReq6
    contEst, contTrans = contadores
    headers = ["vértice A", "vértice B","barrio A","barrio B", "distancia entre A y B"]
    datos = []
    print("La distancia total es de: " + str(distancias))
    print("La cantidad de estaciones que debe visitar son de: " + str(contEst))
    print("La cantidad de transbordos que debe realizar son de: " + str(contTrans))
    for dict in lt.iterator(path):
        verticeA = dict["vertexA"]
        verticeB = dict["vertexB"]
        dist = dict["weight"]
        barrioA = dict["barrioA"]
        barrioB = dict["barrioB"]
        datos.append([verticeA, verticeB, barrioA, barrioB, dist])
    print(tabulate(datos, headers, "grid"))

def printReq7(paths):
    pathI, pathF, cantidades, distancias = paths
    est, trans = cantidades
    distI, distF, distancia = distancias
    headers = ["verticeA", "verticeB", "distancia entre A y B"]
    datosI = []
    datosF = []
    for tupla in lt.iterator(distI):
        verticeA, verticeB, dist = tupla
        datosI.append([verticeA, verticeB, dist])
    for tupla in lt.iterator(distF):
        verticeA, verticeB, dist = tupla
        datosF.append([verticeA, verticeB, dist])
    print("\nEste es el camino de ida")
    print(tabulate(datosI, headers, "grid"))
    print("\nEste es el camino de regreso")
    print(tabulate(datosF, headers, "grid"))
    print("La distancia total es de: " + str(distancia) + " km")
    print("La cantidad de estaciones totales son de: " + str(est))
    print("La cantidad de transbordos que se deben realizar son de: " + str(trans))

def printMenu():
    print("Bienvenido")
    print("1- Cargar información en el catálogo")
    print("2- Buscar un camino posible entre dos estaciones")
    print("3- Buscar el camino con menos paradas")
    print("4- Reconocer los componentes conectados de la Red de rutas de bus")
    print("5- Planear el camino con distancia mínima entre dos puntos geográficos")
    print("6- Informar las estaciones alcanzables desde un origen a un número máximo de conexiones")
    print("7- Buscar el camino con mínima distancia entre una estación de origen y un vecindario de destino")
    print("8- Econtrar un posible camino cinrcular desde una estación de origen")
catalog = None

"""
Menu principal
"""
def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n')
        if int(inputs[0]) == 1:
            print("Cargando información de los archivos ....")
            analyzer = controller.init()
            controller.loadData(analyzer)
            sizeEE, sizeT, sizeA, lonslats = controller.getCargaDeDatos(analyzer)
            printCargaDeDatos(analyzer, sizeEE, sizeT, sizeA, lonslats)

        elif int(inputs[0]) == 2:
            inicio = input("Ingrese el identificador de la estación de inicio: ")
            destino = input("Ingrese el identificador de la estación de destino: ")
            distancia, cant_es, cant_trans, est = controller.buscarCaminoPosible(analyzer, inicio, destino)
            printReq1(distancia, cant_es, cant_trans, est)
        
        elif int(inputs[0]) == 3:
            inicio = input("Ingrese la estación de inicio: ")
            destino = input("Ingrese la estación de destino: ")
            distancia, retorno, estaciones, contador_transbordos = controller.caminoMenosEstaciones(analyzer, inicio, destino)
            printReq2(distancia, retorno, estaciones, contador_transbordos)
        
        elif int(inputs[0]) == 4:
            oficial, size = controller.reconocerComponentesConectados(analyzer)
            printReq3(oficial, size)
        
        elif int(inputs[0]) == 5:
            coordenadasIniciales = input("Ingrese la localización geográfica de origen (longitud, latitud): ")
            coordenadasFinales = input("Ingrese las coordenadas finales (longitud, latitud): ")
            path, estacionI, estacionF, distI, distF, distancia, estaciones, transbordos = controller.estacionesMasCercanas(analyzer, coordenadasIniciales, coordenadasFinales)
            printReq4(path, estacionI, estacionF, distI, distF, distancia, estaciones, transbordos)
        
        elif int(inputs[0]) == 6:
            estI = input("Escriba el identificador de la estación inicial: ")
            cota = input("escriba el número (entero) de conexciones permitidas: ")
            paqueteReq5 = controller.estacionesAlcanzables(analyzer, estI, cota)
            printReq5(paqueteReq5, estI)
        
        elif int(inputs[0]) == 7:
            vecindario = input("Escriba el nombre del vecinadario al que quiere llegar: ")
            estI = input("Escriba el identificador de la estación de origen: ")
            paqueteReq6 = controller.caminoEstacionVecindario(analyzer, estI, vecindario)
            printReq6(paqueteReq6)
        
        elif int(inputs[0]) == 8:
            estI = input("Escriba el identificador de la estación inicial: ")
            paths = controller.recorridoCircular(analyzer, estI)
            printReq7(paths)
        else:
            sys.exit(0)
    sys.exit(0)
if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()