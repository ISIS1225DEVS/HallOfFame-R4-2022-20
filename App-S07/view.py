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
assert cf
from DISClib.ADT import graph as gr
from tabulate import tabulate
import webbrowser
default_limit = 1000
sys.setrecursionlimit(default_limit*10)

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def newController():
    """
    Se crea una instancia del controlador
    """
    control = controller.newController()
    return control

def printTabulatedData(filteredData, headers, detailHeaders=any, firstAndLastThreeDetails = True):
    size = lt.size(filteredData)
    table = []
    width = 19
    if size:
        for data in lt.iterator(filteredData):
            fields = []
            for header in headers:
                if type(data[header]) == dict:
                    detailsTable = []
                    if firstAndLastThreeDetails:
                        filteredDetails = controller.firstAndLastThreeData(data[header])
                    else:
                        filteredDetails = data[header]
                    for register in lt.iterator(filteredDetails):
                        details = []
                        for detailHeader in detailHeaders:
                            if register[detailHeader] == '':
                                details.append('Unknown')
                            else:
                                details.append(register[detailHeader])
                        detailsTable.append(details)
                    fields.append(tabulate(detailsTable, detailHeaders, tablefmt="grid", maxcolwidths=12))
                elif data[header] == '':
                    fields.append('Unknown')
                else:
                    fields.append(data[header])
            table.append(fields)
        if len(headers) <= 4:
            print(tabulate(table, headers, tablefmt="grid") + '\n')
        else:
            print(tabulate(table, headers, tablefmt="grid", maxcolwidths=width) + '\n')
    else:
        print('\nNo se encontró contenido con este criterio de busqueda\n')

def displayMap(generalInformation):
    if generalInformation['Map'] is not None:
        print('\nDo you want to watch the Map?')
        print('\n1- Yes\n2- No')
        answer = input('\nAnswer: ')
        answer = convertAnswer(answer)
        if answer:
            webbrowser.open_new_tab(generalInformation['route'] + '.html')

def convertAnswer(answer):
    converted = False
    if answer in ['1', 1, True, 'True', 'Yes']:
        converted = True
    return converted

def printMenu():
    print("Bienvenido")
    print("0 - Cargar información en el catálogo")
    print("1 - Buscar un camino posible entre dos estaciones")
    print("2 - Buscar el camino con menos paradas entre dos estaciones")
    print("3 - Reconocer los componentes conectados de la Red de rutas de bus")
    print("4 - Planear el camino con distancia mínima entre dos puntos geográficos")
    print("5 - Estaciones alcanzables desde un origen con un número máximo de conexiones dado")
    print("6 - Buscar el camino con distancia mínima entre una estaión de origen y un vecindario de destino")
    print("7 - Encontrar un posible camino circular desde una estación de origen")

analyzer = newController()
sizeFile = '80pct'

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 0:
        print("\n\nCargando información de los archivos ....\n")
        startTime = controller.getTime()
        controller.loadData(analyzer, sizeFile)
        generalInformation = analyzer['generalInformation']
        print('='*5 + ' CSV Loading Specs ' + '='*5)
        print('\nCSV files loaded successfully...\n')
        print('Bus Stops CSV file size: ' + str(generalInformation['busStops']))
        print('Routes CSV file size: ' + str(generalInformation['busEdges']))
        print('\n' + '='*5 + ' Bus-Stops-Routes Processing Stats ' + '='*5)
        print('\n' + '-'*3 + ' Bus-Stops ' + '-'*3)
        print('Exclusive Bus-Stops: ' + str(generalInformation['exclusiveStops']))
        print('Shared Bus-Stops: ' + str(generalInformation['sharedStops']))
        print('Total Bus-Stops: ' + str(gr.numVertices(analyzer['routes'])))
        print('\n' + '-'*3 + ' Bus-Routes ' + '-'*3)
        print('Exclusive Bus-Routes: ' + str(lt.size(analyzer['busEdges'])))
        print('Shared Bus-Routes: ' + str(gr.numEdges(analyzer['diRoutes']) - lt.size(analyzer['busEdges'])))
        print('Total Bus-Routes: ' + str(gr.numEdges(analyzer['diRoutes'])))
        print('\nCreating Graph + DiGraph...')
        print('\n\n' + '='*5 + ' Bus-Stops-Routes DiGraph Specs ' + '='*5)
        print('Digraph Nodes: ' + str(gr.numVertices(analyzer['diRoutes'])))
        print('Digraph Edges: ' + str(gr.numEdges(analyzer['diRoutes'])))
        print('First 5 & Last 5 Bus-Stops loaded in the DiGraph.')
        filtered = controller.firstAndLastFiveData(analyzer['diRoutes'], analyzer['busStops'], True)
        headers = ['Node_ID', 'Code', 'Bus_Stop', 'Transport', 'Longitude', 'Latitude', 'District_Name', 'Neighborhood_Name', 'In Deg', 'Out Deg']
        printTabulatedData(filtered, headers)
        print('='*5 + ' Bus-Stops-Routes Graph Specs ' + '='*5)
        print('Graph Nodes: ' + str(gr.numVertices(analyzer['routes'])))
        print('Graph Edges: ' + str(gr.numEdges(analyzer['routes'])))
        print('First 5 & Last 5 Bus-Stops loaded in the Graph.')
        filtered = controller.firstAndLastFiveData(analyzer['routes'], analyzer['busStops'], False)
        headers = ['Node_ID', 'Code', 'Bus_Stop', 'Transport', 'Longitude', 'Latitude', 'District_Name', 'Neighborhood_Name', 'Degree']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)

    elif int(inputs[0]) == 1:
        stationA = input('Station A: ')
        stationB = input('station B: ')
        startTime = controller.getTime()
        filtered, generalInformation = controller.findPathBetweenTwoStations(analyzer, stationA, stationB)
        print('\n\n' + '='*15 + ' Req No. 1 Inputs ' + '='*15)
        print("Possible path between station '" + stationA + "' and station '" + stationB + "'")
        print('\n' + '='*15 + ' Req No. 1 Answer ' + '='*15)
        print('Total Distance: ' + str(round(generalInformation['distance'], 2)) + ' km.')
        print('Total Stations: ' + str(generalInformation['stations']))
        print('Total Transfers: ' + str(generalInformation['transfers']))
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Paso', 'Departure (Node_ID)', 'Destiny (Node_ID)', 'Distance (km)']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)
        displayMap(generalInformation)
    
    elif int(inputs[0]) == 2:
        stationA = input('Station A: ')
        stationB = input('station B: ')
        startTime = controller.getTime()
        filtered, generalInformation = controller.findShortestPath(analyzer, stationA, stationB)
        print('\n\n' + '='*15 + ' Req No. 2 Inputs ' + '='*15)
        print("Path with fewer stops between station '" + stationA + "' and station '" + stationB + "'")
        print('\n' + '='*15 + ' Req No. 2 Answer ' + '='*15)
        print('Total Distance: ' + str(round(generalInformation['distance'], 2)) + ' km.')
        print('Total Stations: ' + str(generalInformation['stations']))
        print('Total Transfers: ' + str(generalInformation['transfers']))
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Paso', 'Departure (Node_ID)', 'Destiny (Node_ID)', 'Distance (km)']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)
        displayMap(generalInformation)

    elif int(inputs[0]) == 3:
        startTime = controller.getTime()
        filtered, generalInformation = controller.identifyConnectedComponents(analyzer)
        print('\n' + '='*15 + ' Req No. 3 Answer ' + '='*15)
        print('Total connected component: ' + str(generalInformation['connectedComponents']))
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        print('The first five bigest connected components are:')
        headers = ['Number_Component', 'Connected_Component_ID', 'Count', 'Stations']
        detailHeaders = ['Node_ID']
        printTabulatedData(filtered, headers, detailHeaders)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)
        displayMap(generalInformation)
    
    elif int(inputs[0]) == 4:
        longitudeA = float(input('Longitude A: '))
        latitudeA = float(input('Latitude A: '))
        longitudeB = float(input('Longitude B: '))
        latitudeB = float(input('Latitude B: '))
        geolocationA = (longitudeA, latitudeA)
        geolocationB = (longitudeB, latitudeB)
        startTime = controller.getTime()
        filtered, generalInformation = controller.findShortestPathBetweenGeographicPoints(analyzer, geolocationA, geolocationB)
        print('\n\n' + '='*15 + ' Req No. 4 Inputs ' + '='*15)
        print("Shortest path between geolocation '" + str(geolocationA) + "' and geolocation '" + str(geolocationB) + "' by bus routes")
        print('\n' + '='*15 + ' Req No. 4 Answer ' + '='*15)
        print('Distance between Geolocaion A and closet Departure Bus Stop: ' + str(round(generalInformation['geolocationAToStopA'], 2)) + ' km.')
        print('Distance between Departure Bus Stop and Destiny Bus Stop: ' + str(round(generalInformation['distance'], 2)) + ' km.')
        print('Distance between Geolocaion B and closet Destiny Bus Stop: ' + str(round(generalInformation['geolocationBToStopB'], 2)) + ' km.')
        print('Total Stations: ' + str(generalInformation['stations']))
        print('Total Transfers: ' + str(generalInformation['transfers']))
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Paso', 'Departure (Node_ID)', 'Destiny (Node_ID)', 'Distance (km)']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)
        displayMap(generalInformation)

    elif int(inputs[0]) == 5:
        station = input("Estación de origen: ")
        numConnections = int(input("Máximo número de transbordos: "))
        startTime = controller.getTime()
        filtered, generalInformation = controller.locateReachableStations(analyzer, station, numConnections)
        print('\n\n' + '='*15 + ' Req No. 5 Inputs ' + '='*15)
        print("Reachable stations of station '" + station + "' with '" + str(numConnections) + "' maximun connections")
        print('\n' + '='*15 + ' Req No. 5 Answer ' + '='*15)
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Station (Node_ID)','Longitude', 'Latitude', 'long from initial station']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)  
        displayMap(generalInformation)  

    elif int(inputs[0]) == 6:
        station = input("Estación de origen: ")
        neighborhood = input("Vecindario de destino: ")
        startTime = controller.getTime()
        filtered, generalInformation = controller.findShortestPathBetweenStationAndNeighborhood(analyzer, station, neighborhood)
        print('\n\n' + '='*15 + ' Req No. 6 Inputs ' + '='*15)
        print("Shortest path between the station '" + station + "' and the neighborhood '" + neighborhood + "'")
        print('\n' + '='*15 + ' Req No. 6 Answer ' + '='*15)
        print('Total Distance: ' + str(round(generalInformation['distance'], 2)) + ' km.')
        print('Total Stations: ' + str(generalInformation['stations']))
        print('Total Transfers: ' + str(generalInformation['transfers']))
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Paso', 'Departure (Node_ID)', 'Neighborhood Departure', 'Destiny (Node_ID)', 'Neighborhood Destiny', 'Distance (km)']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime) 
        displayMap(generalInformation) 

    elif int(inputs[0]) == 7:
        station = input("Estación de origen: ")
        startTime = controller.getTime()
        filtered, generalInformation = controller.findCircularPath(analyzer, station)
        print('\n\n' + '='*15 + ' Req No. 7 Inputs ' + '='*15)
        print("Circular path from '" + station)
        print('\n' + '='*15 + ' Req No. 7 Answer ' + '='*15)
        print('Total Distance: ' + str(round(generalInformation['distance'], 2)) + ' km.')
        print('Total Stations: ' + str(generalInformation['stations']))
        print('Total Transfers: ' + str(generalInformation['transfers']))
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Paso', 'Departure (Node_ID)', 'Destiny (Node_ID)', 'Distance (km)']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime) 
        displayMap(generalInformation)
        
    else:
        sys.exit(0)
    
    input('\nPulse cualquier tecla para continuar...\n\n')   
sys.exit(0)
