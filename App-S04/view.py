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
import sys
import controller
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import graph as gr
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("Bienvenido")
    print("0- Cargar información en el catálogo")
    print("1- Buscar un camino posible entre dos estaciones")
    print("2- Buscar el camino con menos paradas entre dos estaciones")
    print("3- Reconocer los componentes conectados de la Red de rutas de bus")
    print("4- Planear el camino con distancia mínima entre dos puntos geográficos")
    print("5- Informar las estaciones “alcanzables” desde un origen a un número máximo de conexiones")
    print("6- Buscar el camino con mínima distancia entre una estación de origen y un vecindario de destino")
    print("7- Encontrar un posible camino circular desde una estación de origen")


def loadData(filename):
    stops=controller.loadstops("Barcelona 2/bus_stops_bcn-utf8-" + str(filename)+".csv")
    routes=controller.loadRoute("Barcelona 2/bus_edges_bcn-utf8-" + str(filename)+".csv")
    return stops, routes

def cargaa(catalog):
    lista_usar= catalog[1]['listarutas']
    total_rutas = lista_usar['size']
    print("El total de rutas es de: ")
    print(total_rutas)
    lista_estaciones=catalog[0]['listaestaciones']['elements']
    contador=0
    contador_comp=0
    for i in range(0,len(lista_estaciones)):
        if lista_estaciones[i]['Transbordo']=='N':
            contador+=1
        else:
            contador_comp+=1

    print("El total de estaciones exclusivas es de: ")
    print(contador)
    print("El total de estaciones compartidas es de: ")
    print(contador_comp)
    print("Total de arcos utilizados en todas las rutas de buses es de: ")
    print(catalog[0]['graph']['edges'])
    mayor = 0
    mayor_long=0
    menor_lat= 1000000
    menor_long= 1000000

    for j in range(0,len(lista_estaciones)):
        evaluar= lista_estaciones[j]['Latitude']
        evaluar_long= lista_estaciones[j]['Longitude']

        if float(evaluar) > float(mayor):
            mayor = evaluar

        if float(evaluar_long) > float(mayor_long):
            mayor_long = evaluar_long
        
        if float(evaluar) < float(menor_lat):
            menor_lat = evaluar

        if float(evaluar_long) < float(mayor_long):
            menor_long = evaluar_long
    
    print("Longitud y Latitud Mínima: ")
    print(str(menor_long)+","+str(menor_lat))
    print("Longitud y Latitud Máxima: ")
    print(str(mayor_long)+","+str(mayor))
    print(" ")
    print("Las primeras 5: ")
    for i in range(0,5):
        code = (lista_estaciones[i]['Code'])
        stop = (lista_estaciones[i]['Bus_Stop']).split('-')
        idruta= (str(code)+('-')+stop[1])
        print("ID de la ruta: ")
        print(idruta)
        print("Latitud: ")
        print(lista_estaciones[i]['Latitude'])
        print("Longitud: ")
        print(lista_estaciones[i]['Longitude'])
        print("_________________")

    print(" ")
    print("Las últimas 5: ")
    for i in range(len(lista_estaciones)-5,len(lista_estaciones)):
        code = (lista_estaciones[i]['Code'])
        stop = (lista_estaciones[i]['Bus_Stop']).split('-')
        idruta= (str(code)+('-')+stop[1])
        print("ID de la ruta: ")
        print(idruta)
        print("Latitud: ")
        print(lista_estaciones[i]['Latitude'])
        print("Longitud: ")
        print(lista_estaciones[i]['Longitude'])
        print("_________________")

    print(" ")





def printconectedcomponents(catalog):
    resultado = controller.connectedcomponents(catalog)
    mapacomps = resultado[1]
    organizar = resultado[2]
    for i in range(1, 6):
        llave = (mp.get(mapacomps, organizar[i][0]))
        if llave['value']['size'] > 6:
            print("Componente " + str(organizar[i][0]))
            largo = len(llave['value']['elements'])
            print("El total de componentes conectados es de: " + str(llave['value']['size']))
            for i in range(0,2):
                print(llave['value']['elements'][i])
            for j in range(largo-3, largo):
                print(llave['value']['elements'][j])

        else: 
            print("Componente " + str(organizar[i][0]))
            print("El total de componentes conectados es de: " + str(llave['value']['size']))
            for i in range(0,6):
                print(llave['value']['elements'][i])


"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 0:
        analyzer = controller.newAnalyzer()
        print("Cargando información de los archivos ....")
        filename= "small"
        catalog = loadData(filename)
        catalogonuevo = controller.calculateweight(catalog)
        controller.addEdgesTransbordos(catalogonuevo)
        controller.addStopsBig(catalogonuevo)
        catalogofinal = controller.addEdges(catalogonuevo)
        cargaa(catalogofinal)

    elif int(inputs[0]) == 1:
        initialStation = input("Ingrese la estación incial: ")
        finalStation = input("Ingrese la estación final: ")
        resultado = controller.pathStationsDFS(catalogofinal, initialStation, finalStation)
        print("La distancia total recorrida es: " + str(resultado[1]))
        print("El total de estaciones recorridas es: " + str(resultado[2]))
        print("El total de transbordos es: " + str(resultado[3]))
        print("El camino recorrido es: \n" + str(resultado[0]))


    elif int(inputs[0]) == 2:  
        initialStation = input("Ingrese la estación incial: ")
        finalStation = input("Ingrese la estación final: ")
        resultado = controller.pathStationsBFS(catalogofinal, initialStation, finalStation)
        print("La distancia total recorrida es: " + str(resultado[1]))
        print("El total de estaciones recorridas es: " + str(resultado[2]))
        print("El total de transbordos es: " + str(resultado[3]))
        print("El camino recorrido es: \n" + str(resultado[0]))


    elif int(inputs[0]) == 3:    
        resultado = controller.connectedcomponents(catalogofinal)
        impresion_mapa = controller.connectedcompon(catalogofinal)
        print("El numero de componenetes conectados es de: " + str(resultado[0]))
        printconectedcomponents(catalogofinal)
    
    elif int(inputs[0])==4:
        originlong=input("Ingrese la longitud de la ubicacion inicial: ")
        originlat=input("Ingrese la latitud de la ubicacion inicial: ")
        destlong=input("Ingrese la longitud de la ubicacion destino: ")
        destlat=input("Ingrese la latitud de la ubicacion destino: ")
        resultado=controller.shortestPath(catalogofinal, originlong, originlat, destlong, destlat)
        print("Distancia entre la localización de origen y la estacion de bus más cercano: "+ str(resultado[0]))
        print("Distancia total que le tomará el recorrido entre la estación origen y la estación destino : "+ str(resultado[1]))
        print("Distancia entre la estación destino más cercana y la localización destino: "+ str(resultado[2]))
        print("Total de estaciones que contiene el camino de solución: "+ str(resultado[3]))
        print("Total de transbordos de ruta: "+ str(resultado[4]))

    elif int(inputs[0]) == 5: 
        station = input('Ingrese la estación: ')
        number = input('Ingrese el numero de conexiones permitidas: ')
        print(controller.path_Stations_number(catalog, station, number))

    elif int(inputs[0])== 6:
        estacionorigen=input("Ingrese la estacion origen: ")
        vecindario=input("Ingrese el vecindario al que se quiere dirigir: ")
        resultado=controller.shortestNeighborhood(catalogofinal, estacionorigen, vecindario)
        print("Distancia total que tomará el recorrido entre la estación origen y la estación destino del vecindario destino: "+ str(resultado[0]))
        print("Total de estaciones que contiene el camino de solución: "+ str(resultado[1]))
        print("Total de transbordos de ruta: "+ str(resultado[2]))

    elif int(inputs[0]) == 7: 
        station = input('Ingrese la estación: ')
        resultado = controller.circularPaths(catalog, station)
        print("La distancia total recorrida es: " + str(resultado[1]))
        print("El total de estaciones recorridas es: " + str(resultado[2]))
        print("El total de transbordos es: " + str(resultado[3]))
        print("El camino recorrido es: \n" + str(resultado[0]))

    else:
        sys.exit(0)
sys.exit(0)
