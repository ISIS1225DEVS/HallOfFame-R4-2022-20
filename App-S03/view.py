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
import time 
import sys
import controller
import threading
from DISClib.ADT import list as lt
from tabulate import tabulate 
from DISClib.ADT import list as lt
from DISClib.ADT import graph as gr
assert cf
from DISClib.ADT import map as mp

from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import mapentry as me
assert cf
from prettytable import PrettyTable

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

stopsfile = 'bus_stops_bcn-utf8-large.csv'
edgesfile = 'bus_edges_bcn-utf8-large.csv'
initialStation = None
searchMethod = None


def printMenu():
    print("Bienvenido")
    print("1- Cargar información en el catálogo")
    print("2- Buscar un camino posible entre dos estaciones")
    print("3- Camino con menos paradas entre dos estaciones ")
    print("4- Reconocer los componentes conectados de la Red de rutas de bus ")
    print("5- Planear camino con distancia minima entre dos puntos geograficos ")
    print("6- Localizar las estaciones “alcanzables” desde un origen a un número máximo de conexiones dado")
    print("7- Camino con mínima distancia entre una estación y un vecindario")
    print("8- Encontrar un posible camino circular desde una estación de origen")

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
            cont = controller.init()
            print("\nCargando información de transporte de singapur ....")
            total_exclusivas, total_transbordos,lat_max, lat_min, long_max, long_min =  controller.loadServices(cont, stopsfile, edgesfile)
            
            lista_area = controller.areaRectangular()
            print("El rango del area rectangular de la forma [Longitud minima, Longitud maxima] y [Latitud minima, Latitud maxima] es: ")
            print("Longitudes: [ " +str(long_min) + " " + str(long_max)+"]")
            print("Latitudes: [ " +str(lat_min) + " " + str(lat_max) + "]")
            numedges = controller.totalConnections(cont)
            print("Total de estaciones exclusivas " + str(total_exclusivas) )
            print("Total de transbordos " + str(total_transbordos))
            print('Numero de arcos utilizados: ' + str(numedges))
            
            primeras, ultimas, adj_p, adj_u = controller.primerasyultimas5(cont)
            print('Nota: Key representa el Code-Ruta')
            print('Las 5 primeras estaciones son: ')
            tabla_primeras = PrettyTable(['Identificador estacion', 'Geolocalizacion', 'Numero de estaciones conectadas'])
            for i in range(5):
                tabla_primeras.add_row([lt.getElement(primeras,i+1)['key'],[lt.getElement(primeras,i+1)['value']["Longitude"], lt.getElement(primeras,i+1)['value']["Latitude"]],lt.getElement(adj_p,i+1)])
            print(tabla_primeras)        
            print('')
            print('Las 5 últimas estaciones son: ')
            tabla_ultimas = PrettyTable(['Identificador estacion', 'Geolocalizacion', 'Numero de estaciones conectadas'])
            for i in range(5):
                tabla_ultimas.add_row([lt.getElement(ultimas,i+1)['key'],[lt.getElement(ultimas,i+1)['value']["Longitude"], lt.getElement(ultimas,i+1)['value']["Latitude"]],lt.getElement(adj_u,i+1)])
            print(tabla_ultimas)

        elif int(inputs[0]) == 2:
            #req 1
            station1 = input("Estacion inicial: ")
            station2 = input("Estacion final: ")
            salida, lista_identificadores, lista_distancias, total_transbordos, distancia_total, lista_lat_long = controller.existsPath(cont,station1, station2)
            if salida == None:
                 print("No hay camino entre esas estaciones")
            else: 
                print("Distancia del camino planteado: " + str(distancia_total))
                print("El camino planteado tiene " + str(len(lista_identificadores)) + " estaciones")
                print("El camino planteado tiene " + str(total_transbordos) + " transbordos")
                print("Las estaciones del camino planteado son: ")
                tabla_salida = PrettyTable(['Identificador estacion', 'Distancia a la siguiente estacion'])
                print(len(lista_distancias))
                for i in range(len(lista_identificadores)):
                        tabla_salida.add_row([lista_identificadores[i],lista_distancias[i]])
                print(tabla_salida)
            control = input("Presione 1 si desea ver el mapa de la ruta: ")
            if control == "1":
                controller.crear_mapa(lista_lat_long, lista_identificadores,0)

        elif int(inputs[0]) == 3:
            #req 2
            station1=str(input('estacion inicial: '))
            station2=str(input('estacion final: '))
            salida, lista_identificadores, lista_distancias, total_transbordos, distancia_total, lista_lat_long = controller.shortestPath(cont,station1, station2)
            if salida == None:
                 print("No hay camino entre esas estaciones")
            else: 
                print("Distancia del camino planteado: " + str(distancia_total))
                print("El camino planteado tiene " + str(len(lista_identificadores)) + " estaciones")
                print("El camino planteado tiene " + str(total_transbordos) + " transbordos")
                print("Las estaciones del camino planteado son: ")
                tabla_salida = PrettyTable(['Identificador estacion', 'Distancia a la siguiente estacion'])
                for i in range(len(lista_identificadores)):
                        tabla_salida.add_row([lista_identificadores[i],lista_distancias[i]])
                print(tabla_salida)
            control = input("Presione 1 si desea ver el mapa de la ruta: ")
            if control == "1":
                controller.crear_mapa(lista_lat_long, lista_identificadores,0)

        elif int(inputs[0]) == 4:
            
            start_time = time.time()
            # #req 3
            total, componentes,identificadores = controller.Fconectados(cont)
            end_time = time.time()
            print('-------------------------------------------------------------------------------')
            elapsed_time = end_time - start_time
            print("Elapsed time: " + str(elapsed_time))
            print('\n')
            print('El total de componentes conectados dentro del grafo es: '+str(total))
            print('\n')
            print('-------------------------------------------------------------------------------')
            llaves = om.keySet(componentes)
            # print(str(llaves))
            valores = om.valueSet(componentes)
            for x in range(1,lt.size(llaves)):
                ids = identificadores[str(lt.getElement(valores,x))]
                print('-------------------------------------------------------------------------------')
                print('En el componente ' +str(lt.getElement(valores,x))+' hay '+str(lt.getElement(llaves,x))+' elementos.')
                print('Identificadores de las Primeras tres estaciones en el componente: ')
                for y in [3,2,1]:
                    print(str(lt.getElement(ids,y)))
                print('-------------------------------------------------------------------------------')
                print('Identificadores de las ultimas tres estaciones en el componente: ')
                for y in range(4,lt.size(ids)+1):
                    
                    print(str(lt.getElement(ids,y)))
                print('-------------------------------------------------------------------------------')
            
        elif int(inputs[0]) == 5:
            #req 4
            long1=input('Longitud del origen: ')
            lat1=input('Latitud del origen: ')
            long2=input('Longitud del destino: ')
            lat2=input('Latitud del destino: ')
            distancia_origen, distancia_vertices, distancia_destino, lista_identificadores, lista_distancias, total_transbordos, lista_lat_long = controller.distanciaGeografica(cont, long1, lat1, long2, lat2)
            print("Distancia entre localizacion de origen y estacion de bus mas cercana: " + str(distancia_origen))
            print("Distancia total entre estaciones del recorrido: " + str(distancia_vertices))
            print("Distancia entre estacion destino y localizacion de origen: " + str(distancia_destino))
            print("Total de estaciones del camino: " + str(len(lista_identificadores)-1))
            print("Total de transbordos del camino: " + str(total_transbordos))
            print("Las estaciones del camino planteado son: ")
            tabla_salida = PrettyTable(['Identificador estacion', 'Distancia a la siguiente estacion'])
            for i in range(1,len(lista_identificadores)):
                        tabla_salida.add_row([lista_identificadores[i],lista_distancias[i]])
            print(tabla_salida)
            print(lista_lat_long)
            control = input("Presione 1 si desea ver el mapa de la ruta: ")
            if control == "1":
                controller.crear_mapa(lista_lat_long, lista_identificadores,0)

        elif int(inputs[0]) == 6:
            #req 5
            origen=str(input('estacion de origen: '))
            maxestaciones=int(input('Número de conexiones permitidas desde la estación origen: '))
            estaciones_requeridas, lista_lat_long,conexiones,distancias=controller.estacionesAlcanzables(cont,origen,maxestaciones)
            #total=lt.size(estaciones_requeridas)-1
            #print("Total estaciones alcanzables: " + str(total))
            print("Las estaciones alcanzables son: ")
            print( estaciones_requeridas)
            tabla_salida = PrettyTable(['Identificador estacion', 'latitud', 'longitud', 'conexiones', 'distancias'])
            for i in range(len(estaciones_requeridas)):
                    tabla_salida.add_row([estaciones_requeridas[i],lista_lat_long[i][0],lista_lat_long[i][1],conexiones[i], distancias[i]])
            print(tabla_salida)
            control = input("Presione 1 si desea ver el mapa de la ruta: ")
            if control == "1":
                controller.crear_mapa(lista_lat_long, estaciones_requeridas, 5)

           
            #lt.getElement(estaciones_requeridas,i), lt.getElement(latitudes,i), lt.getElement(longitudes,i), lt.getElement(conexiones,i)
           
            #for valor in lt.iterator(lista):
                #print(valor)
            #print('esta es la lista')
            #print(lista)

        elif int(inputs[0]) == 7:
            #req 6 ana
            origen=str(input('estacion de origen: '))
            vecindario=str(input('vecindario de destino: '))
            salida, lista_identificadores, lista_distancias, total_transbordos, distancia_total, vecindarios, lista_lat_long= controller.distminestacion_vecindario(cont, origen, vecindario)
            if salida == None:
                 print("No hay camino entre esas estaciones")
            else: 
                print("Distancia del camino planteado: " + str(distancia_total))
                print("El camino planteado tiene " + str(len(lista_identificadores)) + " estaciones")
                print("El camino planteado tiene " + str(total_transbordos) + " transbordos")
                print("Las estaciones del camino planteado son: ")
                tabla_salida = PrettyTable(['Identificador estacion', 'Distancia a la siguiente estacion','ID_Vecindario'])
                for i in range(len(lista_identificadores)):
                        tabla_salida.add_row([lista_identificadores[i],lista_distancias[i],vecindarios[i]])
                print(tabla_salida)
            control = input("Presione 1 si desea ver el mapa de la ruta: ")
            if control == "1":
                controller.crear_mapa(lista_lat_long, lista_identificadores,0)
            
        elif int(inputs[0]) == 8:
                estacion = input('Identificador de la estación de origen: ')
                distancia,estaciones,transbordos,camino = controller.circular(cont ,estacion)
                print('la distancia del camino es: '+str(distancia))
                print('el numero de estaciones en el camino es: '+str(estaciones))
                print('el numero de transbordos en el camino es: '+str(transbordos))
                print('el camino que se siguio es: ')
                if camino == None:
                    print('inexistente')
                
       
                else:
                    for m in range(1,lt.size(camino)+1):
                        info = lt.getElement(camino,m)
                        print('Desde Estacion '+ str(info[0])+ ' Hasta Estacion '+ str(info[1])+' Peso a la siguiente estacion: '+ str(info[2]))

        else:
            sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()
