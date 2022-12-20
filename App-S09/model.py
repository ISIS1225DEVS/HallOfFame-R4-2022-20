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
from DISClib.ADT import list as lt
import folium
from folium.plugins import MarkerCluster
import haversine as hv
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import graph as gr
from DISClib.Algorithms.Graphs import dijsktra as dj
from DISClib.Algorithms.Graphs import scc 
from DISClib.Algorithms.Graphs import dfs 
from DISClib.Algorithms.Graphs import bfs
from DISClib.Algorithms.Graphs import cycles as cy
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.ADT import minpq as mpq
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""
def newAnalyzer():
    analyzer = {"stops":None,
                "rutas":None,
                "grafo":None
                }
    analyzer["stops"] = mp.newMap(9300, maptype="PROBING", loadfactor=0.5)
    analyzer["rutas"] = lt.newList("SINGLE_LINKED")
    analyzer["grafo"] = gr.newGraph(datastructure="ADJ_LIST", directed=True, size=15000)
    return analyzer

# Construccion de modelos

# Funciones para agregar informacion al catalogo

def addRutas(analyzer, ruta):
    rutas = analyzer["rutas"]
    lt.addLast(rutas, ruta)

def addStops(analyzer, stop):
    stops = analyzer["stops"]
    nombre = str(stop["Code"])+"-"+str(stop["Bus_Stop"][6:])
    mp.put(stops, nombre, stop)

def addVertices(analyzer):
    grafo = analyzer["grafo"]
    stops = analyzer["stops"]
    for llave in lt.iterator(mp.keySet(stops)):
        entry = mp.get(stops, llave)
        lat = float(me.getValue(entry)["Latitude"])
        lon = float(me.getValue(entry)["Longitude"])
        containsllave = gr.containsVertex(grafo, llave)
        if containsllave == False:
            gr.insertVertex(grafo, llave)
    

def addEdges(analyzer):
    grafo = analyzer["grafo"]
    rutas = analyzer["rutas"]
    for ruta in lt.iterator(rutas):
        code = ruta["Code"]
        parada = ruta["Bus_Stop"]
        destino = ruta["Code_Destiny"]
        vertice1 = str(code)+str(parada[3:])
        vertice2 = str(destino)+str(parada[3:])
        lat1, lon1 = lonAndLat(analyzer, vertice1)
        lat2, lon2 = lonAndLat(analyzer, vertice2)
        distancia = hv.haversine((lat1, lon1), (lat2, lon2))
        containsedge = gr.getEdge(grafo, vertice1, vertice2)
        if containsedge is None:
            gr.addEdge(grafo, vertice1, vertice2, distancia)

def addTransbordos(analyzer):
    stops = analyzer["stops"]
    grafo = analyzer["grafo"]
    for llave in lt.iterator(mp.keySet(stops)):
        entry = mp.get(stops, llave)
        transbordo = me.getValue(entry)["Transbordo"]
        nombre = "T-"+str(me.getValue(entry)["Code"])
        lat = float(me.getValue(entry)["Latitude"])
        lon = float(me.getValue(entry)["Longitude"])
        if transbordo == "S":
            if gr.containsVertex(grafo, nombre) == False:
                gr.insertVertex(grafo, nombre)
                gr.addEdge(grafo, nombre, llave, 0)
                gr.addEdge(grafo, llave, nombre, 0)
            else:
                gr.addEdge(grafo, nombre, llave, 0)
                gr.addEdge(grafo, llave, nombre, 0)
        

def grafoCargaDatos(analyzer):
    mapa = folium.Map(location=[41.3887900, 2.1589900], zoom_start=20)
    stops = analyzer["stops"]
    rutas = analyzer["rutas"]
    coordenadas = []
    codigos = lt.newList("SINGLE_LINKED")
    for llave in lt.iterator(mp.keySet(stops)):
        entry = mp.get(stops, llave)
        codigo = me.getValue(entry)["Code"]
        if lt.isPresent(codigos, codigo) == 0:
            lt.addLast(codigos, codigo)
            lon = float(me.getValue(entry)["Longitude"])
            lat = float(me.getValue(entry)["Latitude"])
            coordenadas.append([lat, lon])
            folium.Marker(location=[lat, lon],icon=folium.Icon(color="green",prefix="fa", icon="bus"), popup=llave).add_to(mapa)
    for ruta in lt.iterator(rutas):
        identificador1 = str(ruta["Code"]) + str(ruta["Bus_Stop"][3:])
        identificador2 = str(ruta["Code_Destiny"]) + str(ruta["Bus_Stop"][3:])
        entry1 =mp.get(stops, identificador1)
        entry2 = mp.get(stops, identificador2)
        coordenadas1 = [float(me.getValue(entry1)["Latitude"]), float(me.getValue(entry1)["Longitude"])]
        coordenadas2 = [float(me.getValue(entry2)["Latitude"]), float(me.getValue(entry2)["Longitude"])]
        folium.PolyLine([coordenadas1, coordenadas2], color="blue", dash_array="5", opacity=".85").add_to(mapa)
    mapa.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapa.html")

# Funciones para creacion de datos

# Funciones de consulta

def getSizeEstacionesExclusivas(analyzer):
    stops = analyzer["stops"]
    contador = 0
    for llave in lt.iterator(mp.keySet(stops)):
        entry = mp.get(stops, llave)
        valor = me.getValue(entry)
        transbordo = valor["Transbordo"]
        if transbordo == "N":
            contador+= 1
    return contador

def getSizeTransbordos(analyzer):
    grafo = analyzer["grafo"]
    contador = 0
    for identificador in lt.iterator(gr.vertices(grafo)):
        if identificador[0] == "T":
            contador += 1
    return contador

def getSizeArcos(analyzer):
    grafo = analyzer["grafo"]
    arcos = gr.edges(grafo)
    return lt.size(arcos)

def getLonAndLatMinMax(analyzer):
    stops = analyzer["stops"]
    lons = []
    lats = []
    for llave in lt.iterator(mp.keySet(stops)):
        entry = mp.get(stops, llave)
        valor = me.getValue(entry)
        lon = valor["Longitude"]
        lat = valor["Latitude"]
        lons.append(float(lon))
        lats.append(float(lat))
    lonMin = min(lons)
    lonMax = max(lons)
    latMin = min(lats)
    latMax = max(lats)
    return lonMin, lonMax, latMin, latMax

def lonAndLat(analyzer, vertice):
    stops = analyzer["stops"]
    entry = mp.get(stops, vertice)
    lat = me.getValue(entry)["Latitude"]
    lon = me.getValue(entry)["Longitude"]
    return float(lat), float(lon)

#Req 1

def buscarCaminoPosible(analyzer, inicio, destino):
    mapa = folium.Map(location=[41.3887900, 2.1589900], zoom_start=50)
    grafo = analyzer["grafo"]
    map = analyzer["stops"]
    transbordos = 0
    estaciones = lt.newList("SINGLE_LINKED")
    estacionesTotales = lt.newList("SINGLE_LINKED")
    search = dj.Dijkstra(grafo, inicio)
    caminoexiste = dj.hasPathTo(search, destino)
    if caminoexiste:
        distancia = dj.distTo(search, destino)
        vertices = dj.pathTo(search, destino)
        for vertice in lt.iterator(vertices):
            grafoReq1(analyzer, vertice, mapa)
            vertexA = vertice["vertexA"]
            vertexB = vertice["vertexB"]
            if vertexA[0] == "T":
                transbordos += 1
            if vertexB[0] == "T":
                transbordos += 1
            entry = mp.get(map, vertexA)
            if entry is not None:
                codigo = me.getValue(entry)["Code"]
                if lt.isPresent(estaciones, codigo) == 0:
                    lt.addLast(estaciones, codigo)
            entry = mp.get(map, vertexB)
            if entry is not None:
                codigo = me.getValue(entry)["Code"]
                if lt.isPresent(estaciones, codigo) == 0:
                    lt.addLast(estaciones, codigo) 
    mapa.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapaReq1.html")           
    return distancia, lt.size(estaciones), transbordos/2, vertices

def grafoReq1(analyzer, vertice, mapa):
    stops = analyzer["stops"]
    verticeA = vertice["vertexA"]
    verticeB = vertice["vertexB"]
    entryA = mp.get(stops, verticeA)
    entryB = mp.get(stops, verticeB)
    if entryA is not None:
        lon = me.getValue(entryA)["Longitude"]
        lat = me.getValue(entryA)["Latitude"]
        marker_cluster = MarkerCluster().add_to(mapa)
        folium.Marker(location=[lat, lon],icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
        if entryB is not None:
            latB = me.getValue(entryB)["Latitude"]
            lonB = me.getValue(entryB)["Longitude"]
            coordenadas1 = [float(lat), float(lon)]
            coordenadas2 = [float(latB), float(lonB)]
            folium.PolyLine([coordenadas1, coordenadas2], color="blue", dash_array="5", opacity=".85").add_to(mapa)

#Req2

def caminoMenosEstaciones(analyzer, inicio, destino):
    mapa = folium.Map(location=[41.3887900, 2.1589900], zoom_start=20)
    grafo = analyzer["grafo"]
    stops = analyzer["stops"]
    contador_transbordos = 0
    buses = lt.newList("SINGLE_LINKED")
    estaciones = lt.newList("SINGLE_LINKED")
    search = bfs.BreadhtFisrtSearch(grafo, inicio)
    existpath = bfs.hasPathTo(search, destino)
    if existpath:
        path = bfs.pathTo(search, destino)
        for identificador in lt.iterator(path):
            entry = mp.get(stops, identificador)
            if entry is not None:
                valor = me.getValue(entry)
                bus_stop = valor["Bus_Stop"]
                if lt.isPresent(buses, bus_stop) == 0:
                    lt.addLast(buses, bus_stop)
                    lt.addLast(estaciones, identificador)
            else:
                lt.addLast(estaciones, identificador)
        for identificador in lt.iterator(estaciones):
            if identificador[0] == "T":
                contador_transbordos += 1
        lt.addLast(estaciones, inicio)
        distancia, retorno = calculadorDistanciasBfs(analyzer, path)
        grafoReq2(analyzer, mapa, retorno)
        mapa.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapaReq2.html")  
    return distancia, retorno, estaciones, contador_transbordos

def calculadorDistanciasBfs(analyzer, path):
    stops = analyzer["stops"]
    grafo = analyzer["grafo"]
    lstcoordenadas = []
    parejaVerticesDistancias = []
    retorno = lt.newList("SINGLE_LINKED")
    distancia = 0
    for identificador in lt.iterator(path):
        entry = mp.get(stops, identificador)
        if entry is not None:
            valor = me.getValue(entry)
            lon = float(valor["Longitude"])
            lat = float(valor["Latitude"])
            coordenadas = (lat, lon)
            lstcoordenadas.append(coordenadas)
            parejaVerticesDistancias.append(identificador)
    for i in range(0, len(lstcoordenadas)-1):
        identificador1 = parejaVerticesDistancias[i]
        identificador2 = parejaVerticesDistancias[i+1]
        dist = hv.haversine(lstcoordenadas[i], lstcoordenadas[i+1])
        distancia += dist
        lt.addLast(retorno, (identificador1, identificador2, dist))
    return distancia, retorno

def grafoReq2(analyzer, mapa, retorno):
    stops  = analyzer["stops"]
    for tupla in lt.iterator(retorno):
        est1, est2, dist = tupla
        entry1 = mp.get(stops, est1)
        entry2 = mp.get(stops, est2)
        if entry1 is not None:
            valor = me.getValue(entry1)
            lat1 = float(valor["Latitude"])
            lon1 = float(valor["Longitude"])
            marker_cluster = MarkerCluster().add_to(mapa)
            folium.Marker(location=[lat1, lon1],icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
            if entry2 is not None:
                valor = me.getValue(entry2)
                lat2 = float(valor["Latitude"])
                lon2 = float(valor["Longitude"])
                coordenadas1 = [lat1, lon1]
                coordenadas2 = [lat2, lon2]
                folium.PolyLine([coordenadas1, coordenadas2], color="blue", dash_array="5", opacity=".85").add_to(mapa)
#Req3

def reconocerComponentesConectados(analyzer):
    grafico = folium.Map(location=[41.3887900, 2.1589900], zoom_start=20)
    grafo = analyzer["grafo"]
    sc = scc.KosarajuSCC(grafo)
    scmarked = sc["marked"]
    marcas = lt.newList("SINGLE_LINKED")
    componentes = sc["idscc"]
    mapa = mp.newMap(maptype="PROBING")
    for llave in lt.iterator(mp.keySet(componentes)):
        entry = mp.get(componentes, llave)
        valor = me.getValue(entry)
        if lt.isPresent(marcas, valor) == 0:
            lt.addLast(marcas, valor)
            lista = lt.newList("SINGLE_LINKED")
            lt.addLast(lista, llave)
            mp.put(mapa, valor, lista)
        else: 
            entry1 = mp.get(mapa, valor)
            lst = me.getValue(entry1)
            lt.addLast(lst, llave)
    oficial = getCC(mapa)
    grafoReq3(analyzer, oficial, grafico)
    grafico.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapaReq3.html")
    return oficial, sc["components"]

def getCC(mapa):
    lista_cc = []
    lista_size = []
    retorno = mp.newMap(maptype="PROBING")
    oficial = mp.newMap(maptype="PROBING")
    for llave in lt.iterator(mp.keySet(mapa)):
        lista_cc.append(llave)
        entry = mp.get(mapa, llave)
        lst = me.getValue(entry)
        size = lt.size(lst)
        lista_size.append(size)
        mp.put(retorno, size, lst)
    lista_size = sorted(lista_size, reverse=True)
    for i in range(0, 5):
        mp.put(oficial, lista_size[i], me.getValue(mp.get(retorno, lista_size[i])))
    return oficial

def grafoReq3(analyzer, oficial, grafico):
    i = 0
    stops = analyzer["stops"]
    colors = ["red", "blue", "black", "green", "pink"]
    coordenadas1 = []
    for llave in lt.iterator(mp.keySet(oficial)):
        coordenadas1 = []
        entry = mp.get(oficial, llave)
        lista = me.getValue(entry)
        for estacion in lt.iterator(lista):
            entryE = mp.get(stops, estacion)
            if entryE is not None:
                valorE = me.getValue(entryE)
                latE = float(valorE["Latitude"])
                lonE = float(valorE["Longitude"])
                coordenada = (latE, lonE)
                coordenadas1.append(coordenada)
                marker_cluster = MarkerCluster().add_to(grafico)
                folium.Marker(location=coordenada,icon=folium.Icon(color=colors[i], icon="ok-sign"),).add_to(marker_cluster)
        i += 1

#Req 4

def estacionMasCercana(analyzer, coordenadasIniciales, coordenadasFinales):
    stops = analyzer["stops"]
    coorI = coordenadasIniciales.split(",")
    coorF = coordenadasFinales.split(",")
    lonI = float(coorI[0].strip())
    latI = float(coorI[1].strip())
    lonF = float(coorF[0].strip())
    latF = float(coorF[1].strip())
    valorReferenciaI = 100000000000000000000000000000
    valorReferenciaF = 100000000000000000000000000000
    for llave in lt.iterator(mp.keySet(stops)):
        entry = mp.get(stops, llave)
        valor = me.getValue(entry)
        lon = float(valor["Longitude"])
        lat = float(valor["Latitude"])
        coor = (lat, lon)
        distanciaI = hv.haversine((latI, lonI),coor)
        if distanciaI < valorReferenciaI:
            valorReferenciaI = distanciaI
            estacionI = llave
        distanciaF = hv.haversine((latF, lonF), coor)
        if distanciaF < valorReferenciaF:
            valorReferenciaF = distanciaF
            estacionF = llave
    return estacionI, estacionF, valorReferenciaI, valorReferenciaF

def recorridoReq4(analyzer, coordenadasIniciales, coordenandasFinales):
    grafico = folium.Map(location=[41.3887900, 2.1589900], zoom_start=10)
    mapa = analyzer["stops"]
    grafo = analyzer["grafo"]
    estaciones = lt.newList("SINGLE_LINKED")
    transbordos = 0
    estacionI, estacionF, distI, distF = estacionMasCercana(analyzer, coordenadasIniciales, coordenandasFinales)
    search = dj.Dijkstra(grafo, estacionI)
    existpath = dj.hasPathTo(search, estacionF)
    if existpath:
        path = dj.pathTo(search, estacionF)
        distancia = dj.distTo(search, estacionF)
        for vertice in lt.iterator(path):
            vertexA = vertice["vertexA"]
            vertexB = vertice["vertexB"]
            if vertexA[0] == "T":
                transbordos += 1
            if vertexB[0] == "T":
                transbordos += 1
            entry = mp.get(mapa, vertexA)
            if entry is not None:
                codigo = me.getValue(entry)["Code"]
                if lt.isPresent(estaciones, codigo) == 0:
                    lt.addLast(estaciones, codigo)
            entry = mp.get(mapa, vertexB)
            if entry is not None:
                codigo = me.getValue(entry)["Code"]
                if lt.isPresent(estaciones, codigo) == 0:
                    lt.addLast(estaciones, codigo)
    grafoReq4(analyzer, grafico, path) 
    grafico.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapaReq4.html")
    return path, estacionI, estacionF, distI, distF, distancia, lt.size(estaciones), transbordos/2

def grafoReq4(analyzer,grafico, path):
    stops = analyzer["stops"]
    for dict in lt.iterator(path):
        verticeA = dict["vertexA"]
        verticeB = dict["vertexB"]
        entryA = mp.get(stops, verticeA)
        entryB = mp.get(stops, verticeB)
        if entryA is not None:
            valorA = me.getValue(entryA)
            coordenadaA = [float(valorA["Latitude"]), float(valorA["Longitude"])]
            marker_cluster = MarkerCluster().add_to(grafico)
            folium.Marker(location=coordenadaA,icon=folium.Icon(color="blue",prefix="fa", icon="bus"),).add_to(marker_cluster)
            if entryB is not None:
                valorB = me.getValue(entryB)
                coordenadaB = [float(valorB["Latitude"]), float(valorB["Longitude"])]
                folium.PolyLine([coordenadaA, coordenadaB], color="blue", dash_array="5", opacity=".85").add_to(grafico)


#Req 5

def estacionesAlcanzables(analyzer,estacionInicial, cota):
    grafico = folium.Map(location=[41.3887900, 2.1589900], zoom_start=10)
    grafo = analyzer["grafo"]
    stops = analyzer["stops"]
    Pestaciones = lt.newList("SINGLE_LINKED")
    estaciones = lt.newList("SINGLE_LINKED")
    lt.addLast(estaciones, estacionInicial)
    if int(cota) != 0:
        primeraOla = gr.adjacents(grafo, estacionInicial)
        lt.addLast(Pestaciones, primeraOla)
        for cada_vertice in lt.iterator(primeraOla):
            lt.addLast(estaciones, cada_vertice)
    for i in range(int(cota)-1):
        lst = lt.newList("SINGLE_LINKED")
        for vertice in lt.iterator(primeraOla):
            ola = gr.adjacents(grafo, vertice)
            lt.addLast(lst, ola)
            for vertice in lt.iterator(ola):
                if lt.isPresent(estaciones, vertice) == 0:
                    lt.addLast(estaciones, vertice)
        lt.addLast(Pestaciones, lst)
    distancias, coordenadasI = distanciasReq5(stops, estaciones, estacionInicial)
    grafoReq5(analyzer, distancias, grafico, coordenadasI)
    grafico.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapaReq5.html")
    return estaciones, lt.size(estaciones), distancias

def distanciasReq5(stops, estaciones, estacionInicial):
    distancias = lt.newList("SINGLE_LINKED")
    entryI = mp.get(stops, estacionInicial)
    centinela = True
    if entryI is not None:
        valorI = me.getValue(entryI)
        coordenadasI = (float(valorI["Latitude"]), float(valorI["Longitude"]))
    else:
        codigo = estacionInicial[2:]+"-"
        while centinela:
            for llave in lt.iterator(mp.keySet(stops)):
                if (codigo[0] == llave[0]) and (codigo in llave):
                    entryI = mp.get(stops, llave)
                    valorI = me.getValue(entryI)
                    coordenadasI = (float(valorI["Latitude"]), float(valorI["Longitude"]))
                    centinela = False
    for cada_estacion in lt.iterator(estaciones):
        entry = mp.get(stops, cada_estacion)
        if entry is not None:
            valor = me.getValue(entry)
            coordenadas = (float(valor["Latitude"]), float(valor["Longitude"]))
            dist = hv.haversine(coordenadasI, coordenadas)
            lt.addLast(distancias, (cada_estacion, dist, coordenadas))
        else:
            coordenadas = "-"
            dist = "-"
            lt.addLast(distancias, (cada_estacion, dist, coordenadas))
    return distancias, coordenadasI

def grafoReq5(analyzer, distancias, grafico, coordenadasI):
    stops = analyzer["stops"]
    coordenadas = []
    marker_cluster = MarkerCluster().add_to(grafico)
    folium.Marker(location=coordenadasI,icon=folium.Icon(color="blue",prefix="fa", icon="bus"),).add_to(marker_cluster)
    for tupla in lt.iterator(distancias):
        est, dist, coord = tupla
        if coord != "-":
            marker_cluster = MarkerCluster().add_to(grafico)
            folium.Marker(location=coord,icon=folium.Icon(color="blue",prefix="fa", icon="bus"),).add_to(marker_cluster)
            folium.PolyLine([coordenadasI, coord], color="blue", dash_array="5", opacity=".85").add_to(grafico)

#Req 6

def caminoEstacionVecindario(analyzer, estacionInicial, vecindario):
    grafico = folium.Map(location=[41.3887900, 2.1589900], zoom_start=20)
    grafo = analyzer["grafo"]
    stops = analyzer["stops"]
    distancia = 100000000000000000000000000000000
    caminos = lt.newList("SINGLE_LINKED")
    search = dj.Dijkstra(grafo, estacionInicial)
    for llave in lt.iterator(mp.keySet(stops)):
        entry = mp.get(stops, llave)
        valor = me.getValue(entry)
        barrio = valor["Neighborhood_Name"]
        if barrio.strip() == vecindario.strip():
            existpath = dj.hasPathTo(search, llave)
            if existpath:
                path = dj.pathTo(search, llave)
                dist = dj.distTo(search, llave)
                if dist < distancia:
                    distancia = dist
                    lt.addLast(caminos, path)
    camino = barrios(stops, lt.lastElement(caminos))
    contadores = totalEstacionesYTransbordos(stops, lt.lastElement(caminos))
    grafoReq6(analyzer, grafico, camino)
    grafico.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapaReq6.html")
    return camino, distancia, contadores

def barrios(stops, path):
    retorno = lt.newList("SINGLE_LINKED")
    for dict in lt.iterator(path):
        dicAuxiliar = {"vertexA":None, "vertexB":None, "weight":None, "barrioA":None, "barrioB":None}
        verticeA = dict["vertexA"]
        verticeB = dict["vertexB"]
        dist = dict["weight"]
        dicAuxiliar["vertexA"] = verticeA
        dicAuxiliar["vertexB"] = verticeB
        dicAuxiliar["weight"] = dist
        entryA= mp.get(stops, verticeA)
        if entryA is not None:
            barrioA = me.getValue(entryA)["Neighborhood_Name"]
        else:
            barrioA = "-"
        entryB = mp.get(stops, verticeB)
        if entryB is not None:
            barrioB = me.getValue(entryB)["Neighborhood_Name"]
        else:
            barrioB = "-"
        dicAuxiliar["barrioA"] = barrioA
        dicAuxiliar["barrioB"] = barrioB
        lt.addLast(retorno, dicAuxiliar)
    return retorno

def totalEstacionesYTransbordos(stops, path):
    contadorEstaciones = 0
    contadorTransbordos = 0
    codigosEstaciones = lt.newList("SINGLE_LINKED")
    for dict in lt.iterator(path):
        verticeA = dict["vertexA"]
        verticeB = dict["vertexB"]
        entryA = mp.get(stops, verticeA)
        entryB = mp.get(stops, verticeB)
        if entryA is not None:
            valorA = me.getValue(entryA)
            if lt.isPresent(codigosEstaciones, valorA["Code"]) == 0:
                lt.addLast(codigosEstaciones, valorA["Code"])
                contadorEstaciones += 1
        else:
            contadorTransbordos += 1
        if entryB is not None:
            valorB = me.getValue(entryB)
            if lt.isPresent(codigosEstaciones, valorB["Code"]) == 0:
                lt.addLast(codigosEstaciones, valorB["Code"])
                contadorEstaciones += 1
        else:
            contadorTransbordos += 1
    return contadorEstaciones, contadorTransbordos/2

def grafoReq6(analyzer, grafico, path):
    stops = analyzer["stops"]
    for dict in lt.iterator(path):
        verticeA = dict["vertexA"]
        verticeB = dict["vertexB"]
        entryA = mp.get(stops, verticeA)
        entryB = mp.get(stops, verticeB)
        if entryA is not None:
            valorA = me.getValue(entryA)
            coordenadaA = [float(valorA["Latitude"]), float(valorA["Longitude"])]
            marker_cluster = MarkerCluster().add_to(grafico)
            folium.Marker(location=coordenadaA,icon=folium.Icon(color="blue",prefix="fa", icon="bus"),).add_to(marker_cluster)
            if entryB is not None:
                valorB = me.getValue(entryB)
                coordenadaB = [float(valorB["Latitude"]), float(valorB["Longitude"])]
                folium.PolyLine([coordenadaA, coordenadaB], color="blue", dash_array="5", opacity=".85").add_to(grafico)

#Req 7

def pathFinal(analyzer, verticeF, estI):
    mapa = analyzer["stops"]
    grafo = analyzer["grafo"]
    searchF = dfs.DepthFirstSearch(grafo, verticeF)
    llaves = mp.keySet(searchF["visited"])
    if lt.isPresent(llaves,estI) != 0:
        return searchF
    else:
        pathFinal(analyzer, verticeF, estI)

def rutaCircular(analyzer, estacionInicial):
    grafico = folium.Map(location=[41.3887900, 2.1589900], zoom_start=15)
    stops = analyzer["stops"]
    grafo = analyzer["grafo"]
    searchI = dfs.DepthFirstSearch(grafo, estacionInicial)
    verticeF = lt.getElement(mp.keySet(searchI["visited"]), 3)
    pathI = dfs.pathTo(searchI, verticeF)
    searchF = pathFinal(analyzer, verticeF, estacionInicial)
    pathF = dfs.pathTo(searchF, estacionInicial)
    cantidades = estacionYTransbordos(analyzer, pathI, pathF)
    coordenadasI = (float(me.getValue(mp.get(stops, estacionInicial))["Latitude"]), float(me.getValue(mp.get(stops, estacionInicial))["Longitude"]))
    idVerticeF = verticeF[2:]+"-"
    if verticeF[0] == "T":
        for llave in lt.iterator(mp.keySet(stops)):
            if (llave[0] == verticeF[2]) and (idVerticeF in llave):
                verticeF = llave
    coordenadasF = (float(me.getValue(mp.get(stops, verticeF))["Latitude"]), float(me.getValue(mp.get(stops, verticeF))["Longitude"]))
    distancias = distanciasReq7(stops, pathI, pathF)
    grafoReq7(analyzer, distancias, grafico)
    marker_cluster = MarkerCluster().add_to(grafico)
    folium.Marker(location=coordenadasI,icon=folium.Icon(color="red",prefix="fa", icon="bus"), popup=estacionInicial).add_to(marker_cluster)
    grafico.save("C:\\Users\\olive\\OneDrive\\Escritorio\\mapaReq7.html")
    return pathI, pathF, cantidades, distancias

def estacionYTransbordos(analyzer, pathI, pathF):
    estaciones = lt.newList()
    transbordos = 0
    stops = analyzer["stops"]
    for estacionI in lt.iterator(pathI):
        entryI = mp.get(stops, estacionI)
        if entryI is not None:
            valor = me.getValue(entryI)
            codigo = valor["Code"]
            if lt.isPresent(estaciones, codigo) == 0:
                lt.addLast(estaciones, codigo)
        else:
            transbordos += 1
    for estacionF in lt.iterator(pathF):
        entryF = mp.get(stops, estacionF)
        if entryF is not None:
            valor = me.getValue(entryF)
            codigo = valor["Code"]
            if lt.isPresent(estaciones, codigo) == 0:
                lt.addLast(estaciones, codigo)
        else:
            transbordos += 1
    return lt.size(estaciones), transbordos/2

def distanciasReq7(stops, pathI, pathF):
    distancia = 0
    distanciasI = lt.newList()
    distanciasF = lt.newList()
    sizeI = lt.size(pathI)
    sizeF = lt.size(pathF)
    centinelaIA = True
    centinelaIB = True
    centinelaFA = True
    centinelaFB = True
    for i in range(sizeI):
        verticeA = lt.getElement(pathI, i)
        verticeB = lt.getElement(pathI, i+1)
        idA = verticeA[2:]
        idB = verticeB[2:]
        entryA = mp.get(stops, verticeA)
        entryB = mp.get(stops, verticeB)
        if entryA is not None:
            valorA = me.getValue(entryA)
            coordenadasA = (float(valorA["Latitude"]), float(valorA["Longitude"]))
        else:
            while centinelaIA:
                for llave in lt.iterator(mp.keySet(stops)):
                    i = mp.get(stops, llave)
                    codigo = me.getValue(i)["Code"]
                    if codigo == idA:
                        centinelaIA = False
                        coordenadasA = (float(me.getValue(i)["Latitude"]), float(me.getValue(i)["Longitude"]))
        if entryB is not None:
            valorB = me.getValue(entryB)
            coordenadasB = (float(valorB["Latitude"]), float(valorB["Longitude"]))
        else: 
            while centinelaIB:
                for llave in lt.iterator(mp.keySet(stops)):
                    i = mp.get(stops, llave)
                    codigo = me.getValue(i)["Code"]
                    if codigo == idB:
                        centinelaIB = False
                        coordenadasB = (float(me.getValue(i)["Latitude"]), float(me.getValue(i)["Longitude"]))
        dist = hv.haversine(coordenadasA, coordenadasB)
        lt.addLast(distanciasI, (verticeA, verticeB, dist))
        distancia += dist
    for i in range(sizeF):
        verticeA = lt.getElement(pathF, i)
        verticeB = lt.getElement(pathF, i+1)
        idA = verticeA[2:]
        idB = verticeB[2:]
        entryA = mp.get(stops, verticeA)
        entryB = mp.get(stops, verticeB)
        if entryA is not None:
            valorA = me.getValue(entryA)
            coordenadasA = (float(valorA["Latitude"]), float(valorA["Longitude"]))
        else:
            while centinelaFA:
                for llave in lt.iterator(mp.keySet(stops)):
                    i = mp.get(stops, llave)
                    codigo = me.getValue(i)["Code"]
                    if codigo == idA:
                        centinelaFA = False
                        coordenadasA = (float(me.getValue(i)["Latitude"]), float(me.getValue(i)["Longitude"]))
        if entryB is not None:
            valorB = me.getValue(entryB)
            coordenadasB = (float(valorB["Latitude"]), float(valorB["Longitude"]))
        else: 
            while centinelaFB:
                for llave in lt.iterator(mp.keySet(stops)):
                    i = mp.get(stops, llave)
                    codigo = me.getValue(i)["Code"]
                    if codigo == idB:
                        centinelaFB = False
                        coordenadasB = (float(me.getValue(i)["Latitude"]), float(me.getValue(i)["Longitude"]))
        dist = hv.haversine(coordenadasA, coordenadasB)
        lt.addLast(distanciasF, (verticeA, verticeB, dist))
        distancia += dist
    return distanciasI, distanciasF, distancia

def grafoReq7(analyzer, distancias, grafico):
    stops = analyzer["stops"]
    distI, distF, dist = distancias
    for tupla in lt.iterator(distI):
        verticeA, verticeB, distancia = tupla
        entryA = mp.get(stops, verticeA)
        entryB = mp.get(stops, verticeB)
        if entryA is not None:
            valorA = me.getValue(entryA)
            coordenadaA = [float(valorA["Latitude"]), float(valorA["Longitude"])]
            marker_cluster = MarkerCluster().add_to(grafico)
            folium.Marker(location=coordenadaA,icon=folium.Icon(color="blue",prefix="fa", icon="bus"),).add_to(marker_cluster)
            if entryB is not None:
                valorB = me.getValue(entryB)
                coordenadaB = [float(valorB["Latitude"]), float(valorB["Longitude"])]
                folium.PolyLine([coordenadaA, coordenadaB], color="blue", dash_array="5", opacity=".85").add_to(grafico)
    for tupla in lt.iterator(distF):
        verticeA, verticeB, distancia = tupla
        entryA = mp.get(stops, verticeA)
        entryB = mp.get(stops, verticeB)
        if entryA is not None:
            valorA = me.getValue(entryA)
            coordenadaA = [float(valorA["Latitude"]), float(valorA["Longitude"])]
            marker_cluster = MarkerCluster().add_to(grafico)
            folium.Marker(location=coordenadaA,icon=folium.Icon(color="blue",prefix="fa", icon="bus"),).add_to(marker_cluster)
            if entryB is not None:
                valorB = me.getValue(entryB)
                coordenadaB = [float(valorB["Latitude"]), float(valorB["Longitude"])]
                folium.PolyLine([coordenadaA, coordenadaB], color="purple", dash_array="5", opacity=".85").add_to(grafico)

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento
