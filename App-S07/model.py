"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
import folium
from folium.plugins import MarkerCluster
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import mergesort as sa
from DISClib.ADT import graph as gr
from math import radians, cos, sin, asin, sqrt
from DISClib.Algorithms.Graphs import dijsktra as dij
from DISClib.Algorithms.Graphs import dfs as dfs
from DISClib.Algorithms.Graphs import bfs as bfs
from DISClib.Algorithms.Graphs import cycles as cy
from DISClib.Algorithms.Graphs import scc as scc
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos
def newAnalyzer(structure):
    analyzer = {}
    analyzer['generalInformation'] = {}
    analyzer['busStops'] = lt.newList(structure)
    analyzer['busEdges'] = lt.newList(structure)
    analyzer['stops'] = mp.newMap(5800, maptype='PROBING')
    analyzer['neighborhoods'] = mp.newMap(100, maptype='PROBING')
    analyzer['routes'] = gr.newGraph(size=5800)
    analyzer['diRoutes'] = gr.newGraph(size=5800, directed=True)
    return analyzer

# Funciones para agregar informacion al catalogo
def addBusStop(analyzer, busStop):
    busStop = updateGeneralInformation(analyzer, busStop)
    idStop = busStop['Node_ID']
    entry = mp.get(analyzer['stops'], idStop)
    if entry is None:
        mp.put(analyzer['stops'], idStop, busStop)
    if not gr.containsVertex(analyzer['routes'], idStop):
        gr.insertVertex(analyzer['routes'], idStop)
        gr.insertVertex(analyzer['diRoutes'], idStop)
    if busStop['Transbordo'] == 'S':
        idTransbordo = busStop['IdTransbordo']
        entry = mp.get(analyzer['stops'], idTransbordo)
        if entry is None:
            mp.put(analyzer['stops'], idTransbordo, busStop)
            count = analyzer['generalInformation'].get('sharedStops', 0)
            analyzer['generalInformation']['sharedStops'] = count + 1
        if not gr.containsVertex(analyzer['routes'], idTransbordo):
            gr.insertVertex(analyzer['routes'], idTransbordo)
            gr.insertVertex(analyzer['diRoutes'], idTransbordo)
    lt.addLast(analyzer['busStops'], busStop)
    addNeighborhood(analyzer, busStop)

def addBusEdge(analyzer, busEdge):
    idStopA = busEdge['Code'] + busEdge['Bus_Stop'].replace('BUS', '')
    idStopB = busEdge['Code_Destiny'] + busEdge['Bus_Stop'].replace('BUS', '')
    entryA, entryB = mp.get(analyzer['stops'], idStopA), mp.get(analyzer['stops'], idStopB)
    if entryA and entryB:
        busStopA, busStopB = me.getValue(entryA), me.getValue(entryB)
        weight = calculateDistance(busStopA, busStopB)
        addEdge(analyzer['routes'], busStopA['Node_ID'], busStopB['Node_ID'], weight)
        addEdge(analyzer['diRoutes'], busStopA['Node_ID'], busStopB['Node_ID'], 1)
        addEdge(analyzer['diRoutes'], busStopB['Node_ID'], busStopA['Node_ID'], 1)
    lt.addLast(analyzer['busEdges'], busEdge)

def connectSharedStops(analyzer):
    for busStop in lt.iterator(analyzer['busStops']):
        if busStop['Transbordo'] == 'S':
            busStop = busStop.copy()
            idStop = busStop['Node_ID']
            idTransbordo = busStop['IdTransbordo']
            addEdge(analyzer['routes'], idStop, idTransbordo, 0)
            addEdge(analyzer['diRoutes'], idStop, idTransbordo, 1)
            addEdge(analyzer['diRoutes'], idTransbordo, idStop, 1)
            busStop['Transport'] = 'Transfer bus'
            busStop['Bus_Stop'] = 'T-BUS'
            busStop['Node_ID'] = idTransbordo
            lt.addLast(analyzer['busStops'], busStop)
            addNeighborhood(analyzer, busStop)

# Funciones para creacion de datos
def updateGeneralInformation(analyzer, busStop):
    idStop = busStop['Code'] + busStop['Bus_Stop'].replace('BUS', '')
    busStop['Node_ID'] = idStop
    if busStop['Transbordo'] == 'S':
        idTransbordo = 'T-' + busStop['Code']
        busStop['IdTransbordo'] = idTransbordo
    else:
        count = analyzer['generalInformation'].get('exclusiveStops', 0)
        analyzer['generalInformation']['exclusiveStops'] = count + 1
    return busStop

def addNeighborhood(analyzer, busStop):
    neighborhoodName = busStop['Neighborhood_Name'].title()
    entry = mp.get(analyzer['neighborhoods'], neighborhoodName)
    if entry is None:
        neighborhood = newNeighborhood(neighborhoodName)
        mp.put(analyzer['neighborhoods'], neighborhoodName, neighborhood)
    else:
        neighborhood = me.getValue(entry)
    lt.addLast(neighborhood['busStops'], busStop['Node_ID'])

def calculateDistance(busStopA, busStopB):
    coordinates = [float(busStopA['Longitude']), float(busStopA['Latitude']), float(busStopB['Longitude']), float(busStopB['Latitude'])]
    longitudeA, latitudeA, longitudeB, latitudeB = map(radians, coordinates)
    deltaLongitude = longitudeB - longitudeA
    deltaLatitude = latitudeB - latitudeA
    a = ((sin(deltaLatitude/2))**2) + (cos(latitudeA) * cos(latitudeB) * ((sin(deltaLongitude/2))**2))
    c = 2 * asin(sqrt(a)) 
    radius = 6371
    distance = c * radius
    return distance

def addEdge(analyzer, stopA, stopB, weight):
    entry = gr.getEdge(analyzer, stopA, stopB)
    if entry is None:
        gr.addEdge(analyzer, stopA, stopB, weight)

def newNeighborhood(neighborhoodName):
    neighborhood = {}
    neighborhood['neighborhood'] = neighborhoodName
    neighborhood['busStops'] = lt.newList()
    return neighborhood

# Funciones de consulta
def findPathBetweenTwoStations(analyzer, stationA, stationB):
    filtered = lt.newList()
    generalInformation = {'distance': 0, 'stations': 0, 'transfers': 0, 'Map': None}
    if mp.contains(analyzer['stops'], stationA) and mp.contains(analyzer['stops'], stationB):
        source = bfs.BreadhtFisrtSearch(analyzer['routes'], stationA)
        if bfs.hasPathTo(source, stationB):
            route = bfs.pathTo(source, stationB)
            generalInformation['stations'] = lt.size(route)
            departure = lt.removeLast(route)
            i = 1
            while lt.size(route) > 0:
                if 'T-' in departure:
                    generalInformation['transfers'] += 1
                destiny = lt.lastElement(route)
                distance = gr.getEdge(analyzer['routes'], departure, destiny)['weight']
                path = {'Paso': i, 'Departure (Node_ID)': departure, 'Destiny (Node_ID)': destiny, 'Distance (km)': round(distance, 2)}
                lt.addLast(filtered, path)
                departure = lt.removeLast(route)
                generalInformation['distance'] += distance
                i += 1
                if lt.size(route) == 0:
                    path = {'Paso': i, 'Departure (Node_ID)': destiny, 'Destiny (Node_ID)': 'Finished', 'Distance (km)': 0}
                    lt.addLast(filtered, path)
            if 'T-' in stationB:
                generalInformation['transfers'] += 1
            generalInformation['Map'] = True
    route = 'Possible Path Between Two Stations'
    createMap(analyzer, filtered, 'Departure (Node_ID)', route)
    generalInformation['route'] = route
    return filtered, generalInformation

def findShortestPath(analyzer, stationA, stationB, type='diRoutes'):
    filtered = lt.newList()
    generalInformation = {'distance': 0, 'stations': 0, 'transfers': 0, 'Map': None}
    if mp.contains(analyzer['stops'], stationA) and mp.contains(analyzer['stops'], stationB):
        source = dij.Dijkstra(analyzer[type], stationA)
        if dij.hasPathTo(source, stationB):
            route = dij.pathTo(source, stationB)
            i = lt.size(route)
            for step in lt.iterator(route):
                departure = step['vertexA']
                destiny = step['vertexB']
                distance = gr.getEdge(analyzer['routes'], departure, destiny)['weight']
                path = {'Paso': i, 'Departure (Node_ID)': departure, 'Destiny (Node_ID)': destiny, 'Distance (km)': round(distance, 2)}
                lt.addFirst(filtered, path)
                generalInformation['distance'] += distance
                if 'T-' in departure:
                    generalInformation['transfers'] += 1
                i -= 1
            if lt.size(filtered) > 0:
                path = {'Paso': lt.size(route) + 1, 'Departure (Node_ID)': lt.firstElement(route)['vertexB'], 'Destiny (Node_ID)': 'Finished', 'Distance (km)': 0}
                lt.addLast(filtered, path)
            if 'T-' in stationB:
                generalInformation['transfers'] += 1
            if lt.size(route) == 0:
                generalInformation['stations'] = lt.size(route)
            else:
                generalInformation['stations'] = lt.size(route) + 1
            generalInformation['Map'] = True
    route = 'Path With Fewer Stops Between Two Stations'
    createMap(analyzer, filtered, 'Departure (Node_ID)', route)
    generalInformation['route'] = route
    return filtered, generalInformation

def identifyConnectedComponents(analyzer):
    filtered = lt.newList()
    map = mp.newMap(5731, maptype='PROBING')
    generalInformation = {'connectedComponents': 0, 'Map': None}
    source = scc.KosarajuSCC(analyzer['routes'])
    connectedComponents = source['idscc']
    for component in lt.iterator(mp.keySet(connectedComponents)):
        connectedComponentID = mp.get(connectedComponents, component)
        lt.addLast(filtered, connectedComponentID)
        addConnectedComponent(analyzer, map, connectedComponentID)
    generalInformation['Map'] = True
    route = 'Connected Components'
    createMap(analyzer, filtered, 'key', route)
    generalInformation['route'] = route
    filtered = mp.valueSet(map)
    sortRegisters(filtered, compareReq3)
    generalInformation['connectedComponents'] = scc.connectedComponents(source)
    Top5Components = lt.newList()
    N = 5
    if lt.size(filtered) < 5:
        N = lt.size(filtered)
    for i in range(1, N+1):
        register = lt.removeFirst(filtered)
        register['Number_Component'] = i
        lt.addLast(Top5Components, register)
    return Top5Components, generalInformation

def findShortestPathBetweenGeographicPoints(analyzer, geolocationA, geolocationB):
    filtered = lt.newList()
    generalInformation = {'distance': 0, 'stations': 0, 'transfers': 0, 'Map': None}
    geolocation = convertGeolocation(analyzer, geolocationA, geolocationB)
    generalInformation['geolocationAToStopA'] = geolocation['distanceA']
    generalInformation['geolocationBToStopB'] = geolocation['distanceB']
    if (mp.contains(analyzer['stops'], geolocation['busStopA'])) and (mp.contains(analyzer['stops'], geolocation['busStopB'])):
        source = dij.Dijkstra(analyzer['routes'], geolocation['busStopA'])
        if dij.hasPathTo(source, geolocation['busStopB']):
            route = dij.pathTo(source, geolocation['busStopB'])
            i = lt.size(route) + 1
            for step in lt.iterator(route):
                departure = step['vertexA']
                destiny = step['vertexB']
                distance = gr.getEdge(analyzer['routes'], departure, destiny)['weight']
                path = {'Paso': i, 'Departure (Node_ID)': departure, 'Destiny (Node_ID)': destiny, 'Distance (km)': round(distance, 2)}
                lt.addFirst(filtered, path)
                generalInformation['distance'] += distance
                if 'T-' in departure:
                    generalInformation['transfers'] += 1
                i -= 1
            updateCounts(generalInformation, geolocation['busStopB'], lt.size(route))
            generalInformation['Map'] = True
    addGeographicPoints(analyzer, filtered, geolocation, geolocationA, geolocationB)
    route = 'Shortest Path between Between Two Geograpich Points By Bus Routes'
    createMap(analyzer, filtered, 'Departure (Node_ID)', route)
    generalInformation['route'] = route
    return filtered, generalInformation

def locateReachableStations(analyzer, station, numConnections):
    filtered = lt.newList()
    generalInformation = {'Map': None}
    if mp.contains(analyzer['stops'], station):
        stations = [station]
        addReachableStation(analyzer, station, filtered, 1, numConnections, stations)
        generalInformation['Map'] = True
    sortRegisters(filtered, compareLongs)
    route = 'Reachable Stations of a Station With a Number of Connections'
    createMap(analyzer, filtered, 'Station (Node_ID)', route)
    generalInformation['route'] = route
    return filtered, generalInformation

def findShortestPathBetweenStationAndNeighborhood(analyzer, station, neighborhood):
    entry = mp.get(analyzer['neighborhoods'], neighborhood)
    filtered = lt.newList()
    generalInformation = {'distance': 0, 'stations': 0, 'transfers': 0, 'Map': None}
    if (entry) and (mp.contains(analyzer['stops'], station)):
        busStops = me.getValue(entry)['busStops']
        source = dij.Dijkstra(analyzer['routes'], station)
        stationsInformation = {'station': None, 'distance': float('inf')}
        for busStop in lt.iterator(busStops):
            if dij.hasPathTo(source, busStop):
                distance = dij.distTo(source, busStop)
                if distance < stationsInformation['distance']:
                    stationsInformation['distance'] = distance
                    stationsInformation['station'] = busStop
        if dij.hasPathTo(source, stationsInformation['station']):
            route = dij.pathTo(source, stationsInformation['station'])
            i = lt.size(route)
            for step in lt.iterator(route):
                departure = step['vertexA']
                destiny = step['vertexB']
                if mp.get(analyzer['stops'], departure)['value']['Neighborhood_Name'].title() != neighborhood:
                    distance = gr.getEdge(analyzer['routes'], departure, destiny)['weight']
                    path = {'Paso': i, 'Departure (Node_ID)': departure, 'Neighborhood Departure': mp.get(analyzer['stops'], departure)['value']['Neighborhood_Name'], 'Destiny (Node_ID)': destiny, 'Neighborhood Destiny': mp.get(analyzer['stops'], destiny)['value']['Neighborhood_Name'], 'Distance (km)': round(distance, 2)}
                    lt.addFirst(filtered, path)
                    generalInformation['distance'] += distance
                    if 'T-' in departure:
                        generalInformation['transfers'] += 1
                    i -= 1
            if lt.size(filtered) > 0:
                departure = lt.firstElement(route)['vertexB']
                path = {'Paso': lt.size(route) + 1, 'Departure (Node_ID)': departure, 'Neighborhood Departure': mp.get(analyzer['stops'], departure)['value']['Neighborhood_Name'], 'Destiny (Node_ID)': 'Finished', 'Neighborhood Destiny': 'Finished', 'Distance (km)': 0}
                lt.addLast(filtered, path)
            if 'T-' in stationsInformation['station']:
                generalInformation['transfers'] += 1
            if lt.size(route) == 0:
                generalInformation['stations'] = lt.size(route)
            else:
                generalInformation['stations'] = lt.size(route) + 1
            generalInformation['Map'] = True
    route = 'Shortest Path Between a Station and a Neighborhood'
    createMap(analyzer, filtered, 'Departure (Node_ID)', route)
    generalInformation['route'] = route
    return filtered, generalInformation

def findCircularPath(analyzer, initialStation):
    filtered = lt.newList()
    findedPath = lt.newList()
    generalInformation = {'distance': 0, 'stations': 0, 'transfers': 0, 'Map': None}
    if mp.contains(analyzer['stops'], initialStation):
        lt.addLast(filtered, initialStation)
        addCircularPath(analyzer, filtered, findedPath, initialStation, initialStation, generalInformation, 1)
        generalInformation['Map'] = True
    if lt.size(findedPath) == 0:
        generalInformation['stations'] = lt.size(findedPath)
    else:
        generalInformation['stations'] = lt.size(findedPath) + 1
    if lt.size(filtered) > 0:
        distance = gr.getEdge(analyzer['routes'], lt.lastElement(filtered), initialStation)['weight']
        step = {'Paso': lt.size(filtered), 'Departure (Node_ID)': lt.lastElement(filtered), 'Destiny (Node_ID)': initialStation, 'Distance (km)': round(distance, 2)}
        lt.addLast(findedPath, step)
        route = 'Circular Path From a Station'
        createMap(analyzer, findedPath, 'Departure (Node_ID)', route)
        generalInformation['route'] = route
        step = {'Paso': lt.size(filtered) + 1, 'Departure (Node_ID)': lt.lastElement(filtered), 'Destiny (Node_ID)': 'Finished', 'Distance (km)': 0}
        lt.addLast(findedPath, step)
        generalInformation['distance'] += distance
        if 'T-' in lt.lastElement(filtered):
            generalInformation['transfers'] += 1
    return findedPath, generalInformation

def createMap(analyzer, filtered, reachRoute, route):
    map = folium.Map(location=[41.38879, 2.15899], zoom_start=6)
    mark = MarkerCluster()
    for register in lt.iterator(filtered):
        busStop = mp.get(analyzer['stops'], register[reachRoute])['value']
        coordinates = [float(busStop['Latitude']), float(busStop['Longitude'])]
        label = ''
        if register.get('Paso', None) != None:
            label = 'PASO ' + str(register['Paso']) + '\n'
        if register.get('value', None) != None:
            label = 'Component ID: ' + str(register['value']) + '\n'
        for key, value in busStop.items():
            label += str(key) + ': ' + str(value) + ' \n'
        mark.add_child(folium.Marker(location=coordinates, popup=label))
    map.add_child(mark)
    map.save(route + '.html')

# Funciones de soporte para las consultas
def addConnectedComponent(analyzer, map, component):
    station, componentID = component['key'], component['value']
    entry = mp.get(map, componentID)
    if entry is None:
        connectedComponent = newConnectedComponent(componentID)
        mp.put(map, componentID, connectedComponent)
    else:
        connectedComponent = me.getValue(entry)
    busStop = mp.get(analyzer['stops'], station)['value']
    connectedComponent['Count'] += 1
    lt.addLast(connectedComponent['Stations'], busStop)

def newConnectedComponent(componentID):
    connectedcomponent = {}
    connectedcomponent['Connected_Component_ID'] = componentID
    connectedcomponent['Count'] = 0
    connectedcomponent['Stations'] = lt.newList()
    return connectedcomponent

def convertGeolocation(analyzer, geolocationA, geolocationB):
    geolocationA = convertCoordinates(geolocationA)
    geolocationB = convertCoordinates(geolocationB)
    geolocation = {'busStopA': None ,'distanceA': float('inf'), 'busStopB': None, 'distanceB': float('inf')}
    for busStopKey in lt.iterator(mp.keySet(analyzer['stops'])):
        busStop = mp.get(analyzer['stops'], busStopKey)['value']
        distance = calculateDistance(busStop, geolocationA)
        if distance < geolocation['distanceA']:
            geolocation['distanceA'] = distance
            geolocation['busStopA'] = busStopKey
        distance = calculateDistance(busStop, geolocationB)
        if distance < geolocation['distanceB']:
            geolocation['distanceB'] = distance
            geolocation['busStopB'] = busStopKey
    return geolocation

def convertCoordinates(coordinates):
    return {'Longitude': coordinates[0], 'Latitude': coordinates[1]}

def addGeographicPoints(analyzer, filtered, geolocation, geolocationA, geolocationB):
    if lt.size(filtered) > 0:
        destinyA = lt.firstElement(filtered)['Destiny (Node_ID)']
        path = {'Paso': 1, 'Departure (Node_ID)': str(geolocationA), 'Destiny (Node_ID)': destinyA, 'Distance (km)': round(geolocation['distanceA'], 2)}
        lt.addFirst(filtered, path)
        departureB = lt.lastElement(filtered)['Destiny (Node_ID)']
        path = {'Paso': lt.size(filtered) + 1, 'Departure (Node_ID)': departureB, 'Destiny (Node_ID)': str(geolocationB), 'Distance (km)': round(geolocation['distanceA'], 2)}
        lt.addLast(filtered, path)
        path = {'Paso': lt.size(filtered) + 1, 'Departure (Node_ID)': str(geolocationB), 'Destiny (Node_ID)': 'Finished', 'Distance (km)': 0}
        lt.addLast(filtered, path)
        mp.put(analyzer['stops'], str(geolocationA), {'Reference': 'Geographic Point A', 'Longitude': geolocationA[0], 'Latitude': geolocationA[1]})
        mp.put(analyzer['stops'], str(geolocationB), {'Reference': 'Geographic Point B', 'Longitude': geolocationB[0], 'Latitude': geolocationB[1]})

def addReachableStation(analyzer, station, listStations,numStation, numConnections, stations):
    if numStation <= numConnections:
        reachableStations = gr.adjacents(analyzer['routes'], station)
        for reachableStation in lt.iterator(reachableStations):
            busStop = mp.get(analyzer['stops'], reachableStation)['value']
            if reachableStation not in stations:
                stations.append(reachableStation)
                lt.addLast(listStations, {'Station (Node_ID)': reachableStation, 'long from initial station': numStation, 'Longitude': busStop['Longitude'], 'Latitude': busStop['Latitude']})
                addReachableStation(analyzer, reachableStation, listStations, numStation+1, numConnections, stations)
        numStation += 1

def updateCounts(generalInformation, destiny, sizeRoute):
    if sizeRoute == 0:
        generalInformation['stations'] = 0
    else:
        generalInformation['stations'] = sizeRoute + 1
        if 'T-' in destiny:
            generalInformation['transfers'] += 1

def updateDatum(datum, analyzer, directed):
    if directed:
        datum['In Deg'] = gr.indegree(analyzer, datum['Node_ID'])
        datum['Out Deg'] = gr.outdegree(analyzer, datum['Node_ID'])
    else:
        datum['Degree'] = gr.degree(analyzer, datum['Node_ID'])
    return datum

def addCircularPath(analyzer, filtered, findedPath, initialStation, station, generalInformation, i):
    reachableStations = gr.adjacents(analyzer['routes'], station)
    for reachableStation in lt.iterator(reachableStations):
        if (reachableStation != initialStation) and (gr.getEdge(analyzer['routes'], lt.lastElement(filtered), reachableStation) is not None) and (gr.getEdge(analyzer['routes'], initialStation, reachableStation) is not None):
            departure = lt.lastElement(filtered)
            destiny = reachableStation
            distance = gr.getEdge(analyzer['routes'], departure, destiny)['weight']
            path = {'Paso': i, 'Departure (Node_ID)': departure, 'Destiny (Node_ID)': destiny, 'Distance (km)': round(distance, 2)}
            generalInformation['distance'] += distance
            lt.addLast(filtered, reachableStation)
            lt.addLast(findedPath, path)
            i += 1
            if 'T-' in departure:
                generalInformation['transfers'] += 1
            addCircularPath(analyzer, filtered, findedPath, initialStation, reachableStation, generalInformation, i)

# Funciones utilizadas para comparar elementos dentro de una lista
def compareReq3(registerA, registerB):
    if int(registerA['Count']) == int(registerB['Count']):
        return compareIDs(registerA, registerB)
    else:
        return compareCounts(registerA, registerB)

def compareLongs(registerA, registerB):
    return (int(registerA['long from initial station']) < int(registerB['long from initial station']))

def compareValues(registerA, registerB):
    return (int(registerA['value']) > int(registerB['value']))

def compareSizes(registerA, registerB):
    return (int(registerA['size']) > int(registerB['size']))

def compareCounts(registerA, registerB):
    return (int(registerA['Count']) > int(registerB['Count']))

def compareIDs(registerA, registerB):
    return (int(registerA['Connected_Component_ID']) < int(registerB['Connected_Component_ID']))

#def compare

# Funciones de ordenamiento
def firstAndLastThreeData(lista):
    filteredData = lt.newList()
    size = lt.size(lista)
    if size >= 1:
        if size <= 6:
            filteredData = lista
        else:
            for pos in range(1, 4):
                datum = lt.getElement(lista, pos)
                lt.addLast(filteredData, datum)
            for pos in range(size-2, size+1):
                datum = lt.getElement(lista, pos)
                lt.addLast(filteredData, datum)
    return filteredData

def firstAndLastFiveData(analyzer, lista, directed=False):
    filteredData = lt.newList()
    size = lt.size(lista)
    if size >= 1:
        if size <= 10:
            for datum in lt.iterator(lista):
                datum = updateDatum(datum, analyzer, directed)
            filteredData = lista
        else:
            for pos in range(1, 6):
                datum = lt.getElement(lista, pos)
                datum = updateDatum(datum, analyzer, directed)
                lt.addLast(filteredData, datum)
            for pos in range(size-4, size+1):
                datum = lt.getElement(lista, pos)
                datum = updateDatum(datum, analyzer, directed)
                lt.addLast(filteredData, datum)
    return filteredData

def sortRegisters(lista, compareReq):
    return sa.sort(lista, compareReq)