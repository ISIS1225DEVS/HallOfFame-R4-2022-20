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

import controller
import config as cf

from tabulate import tabulate
import threading
import sys

assert cf

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("\n********************")
    print("**** BIENVENIDO ****")
    print("********************\n")

    print("0- Cargar información en el catálogo")
    print("1- Buscar un camino posible entre dos estaciones")
    print("2- Buscar el camino con menos paradas entre dos estaciones")
    print("3- Reconocer los componentes conectados de la Red de rutas de bus")
    print("4- Planear el camino con distancia mínima entre dos puntos geográficos")
    print("5- Informar las estaciones alcanzables desde un origen a un número máximo de conexiones")
    print("6- Buscar el camino con mínima distancia entre una estación de origen y un vecindario de destino")
    print("7- Encontrar un posible camino circular desde una estación de origen")
    print("8- Test de espacio")
    print("9- Test de memoria")

def printDataSize():
    print("\n********************")
    print("****  OPCIONES  ****")
    print("********************\n")
    print("1.) small")
    print("2.) 5 pct")
    print("3.) 10 pct")
    print("4.) 20 pct")
    print("5.) 30 pct")
    print("6.) 50 pct")
    print("7.) 80 pct")
    print("8.) large\n")

catalog = None

"""
Menu principal
"""
while True:
    printMenu()
    print('Seleccione una opción para continuar')
    inputs = input("$> ")
    if int(inputs[0]) == 0:
        print("Cargando información de los archivos ....")
        printDataSize()
        pct = int(input("pct> "))
        size = ["small", "5pct", "10pct", "20pct", "30pct", "50pct", "80pct", "large"]
        catalog = controller.initCatalog()
        stations_u, stations_c, total_vertices, buses_u, buses_c, total_edges, output = controller.loadData(catalog, size[pct-1])
        print("---Bus-Stops---")
        print(f"Exclusive Bus-Stops: {stations_u}")
        print(f"Shared Bus-Stops: {stations_c}")
        print(f"Total Bus-Stops: {total_vertices}\n")
        print("---Bus-Routes---")
        print(f"Exclusive Bus-Routes: {buses_u}")
        print(f"Shared Bus-Routes: {buses_c}")
        print(f"Total Bus-Routes: {total_edges}\n")
        print(tabulate(output, headers="keys", tablefmt="grid"))

    elif int(inputs[0]) == 1:
        print("---Requerimiento 1 - Buscar un camino posible entre dos estaciones---")
        station_i = input("Ingrese su estacion inicial: ")
        station_f = input("Ingrese su estacion final: ")
        distance, station_f, stations_t, tranfers_t, steps = controller.routeStations(catalog, station_i, station_f)
        print(f"La distancia entre las estaciones {station_i} y {station_f} es de {distance} Km")
        print(f"La ruta contiene {stations_t} estaciones y {tranfers_t} transbordos. \n")
        print("La ruta es la siguiente: \n")
        print(tabulate(steps, headers="keys", tablefmt="grid"))

    elif int(inputs[0]) == 2:
        print("---Requerimiento 2 - Buscar el camino con menos paradas entre dos estaciones---")
        station_i = input("Ingrese la estacion de origen: ")
        station_f = input("Ingrese la estacion de destino: ")
        distance_t, stations_t, tranfers_t, steps = controller.fewStops(catalog, station_i, station_f)
        print(f"La distancia entre las estaciones {station_i} y {station_f} es de {distance_t} Km")
        print(f"La ruta contiene {stations_t} estaciones y {tranfers_t} transbordos. \n")
        print("La ruta es la siguiente: \n")
        print(tabulate(steps, headers="keys", tablefmt="grid"))

    elif int(inputs[0]) == 3:
        print('---Requerimiento 3 - Conocer si existen componentes conectados en el grafo, cuantos son y sus caracteristicas---')
        print('El numero de componentes conectados es: '+ str(controller.connectedComponents(catalog)))
        print(f'Los 5 Componentes conectados más grandes')

    elif int(inputs[0]) == 4:
        print("---Requerimiento 4 - Planear el camino con distancia mínima entre dos puntos geográficos---")
        lon_i = float(input("Ingrese la longitud inicial: "))
        lat_i = float(input("Ingrese la latitud inicial: "))
        lon_f = float(input("Ingrese la longitud final: "))
        lat_f = float(input("Ingrese la latitud final: "))
        station_i, distance_i, station_f, distance_f, distance_t, stations_t, tranfers_t, steps = controller.planShortRoute(catalog, lon_i, lat_i, lon_f, lat_f)
        print(f"La estacion inicial mas cercana es {station_i} y esta a {distance_i} Km del inicio")
        print(f"La estacion final mas cercana es {station_f} y esta a {distance_f} Km del destino")
        print(f"La distancia total del viaje entre la estacion inicial y la estacion final es de {distance_t} Km")
        print(f"Se viaja a traves de {stations_t} estaciones y se realizan {tranfers_t} transbordos\n")
        print("El camino a seguir es: \n")
        print(tabulate(steps, headers="keys", tablefmt="grid"))

    elif int(inputs[0]) == 5:
        print("---Requerimiento 5 - Informar las estaciones alcanzables desde un origen a un número máximo de conexiones---")
        id_org = input("Identificador de la estacion origen: ")
        num_max = int(input("Numero de conexiones permitidas desde la estación origen: "))
        format_list = controller.reachable_stations(catalog, id_org, num_max)
        print(tabulate(format_list, headers="keys", tablefmt="grid"))

    elif int(inputs[0]) == 6:
        print("---Requerimiento 6 - Buscar el camino con mínima distancia entre una estación de origen y un vecindario de destino---")
        station_i = input("Ingrese su estacion inicial: ")
        nh = input("Ingrese su vecindario: ")
        distance, station_f, stations_t, tranfers_t, steps = controller.routeStationNH(catalog, station_i, nh)
        print(f"La distancia entre las estaciones {station_i} y {station_f} es de {distance} Km")
        print(f"La ruta contiene {stations_t} estaciones y {tranfers_t} transbordos. \n")
        print("La ruta es la siguiente: \n")
        print(tabulate(steps, headers="keys", tablefmt="grid"))

    elif int(inputs[0]) == 7:
        print("---Requerimiento 7 - Encontrar un posible camino circular desde una estación de origen---")
        station = input("Ingrese la estacion de origen (Code-IdBus): ")
        distance, stations_t, tranfers_t, steps_i, steps_f = controller.circularPath(catalog, station)
        print(f"Es recorrido desde la estacion {station} es de {distance} Km")
        print(f"El numero total de estaciones es de {stations_t} estaciones y de {tranfers_t} transbordos")
        print("La ruta circular de ida es: ")
        print(tabulate(steps_i, headers="keys", tablefmt="grid"))
        print("La ruta circular de vuelta es: ")
        print(tabulate(steps_f, headers="keys", tablefmt="grid"))

    elif int(inputs[0]) == 8:
        for i in range(1,8):
            tiempo = controller.runReqTests(i, catalog)
            print(f"Para el requerimiento {i} se ha demorado {tiempo}")

    elif int(inputs[0]) == 9:
        for i in range(1,8):
            tiempo = controller.runMemoryTest(i, catalog)
            print(f"Para el requerimiento {i} se ha gastado {tiempo}")

    else:
        sys.exit(0)


if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()
