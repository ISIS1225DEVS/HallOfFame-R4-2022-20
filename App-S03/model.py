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
from math import radians, cos, sin, asin, sqrt
from DISClib.ADT import list as lt

from DISClib.ADT import map as m
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa

from DISClib.Algorithms.Sorting import quicksort as quick
from DISClib.ADT import graph as gr
from DISClib.Algorithms.Graphs import scc as scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import dfs 

from DISClib.Algorithms.Graphs import cycles 
from DISClib.Algorithms.Graphs import bfs 
from DISClib.Utils import error as error
from DISClib.ADT import orderedmap as om
from DISClib.Algorithms.Sorting import mergesort as merge
from DISClib.ADT import stack as stk
import folium
import webbrowser

assert cf


"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""
lat_max = 0
lat_min = 100
long_max = 0
long_min = 100

# Construccion de modelos

def newAnalyzer():
    
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        
        analyzer = {
            'vertices': None,
            'transbordos': None,
            'grafo': None,
            'conexos': None,
            'posibles': None,
            'cortos_saltos':None, 
            'cortos_peso': None,
            'vecindarios':None,
            'arbol_long_lat': None
        }

        analyzer['transbordos'] = m.newMap(numelements= 1000, maptype ='CHAINING',
                                    comparefunction = compareStopIds) 
        analyzer['vertices'] = m.newMap(numelements= 1000, maptype ='CHAINING',
                                    comparefunction = compareStopIds) 

        analyzer['grafo'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareStopIds)                                
        analyzer["vecindarios"] = m.newMap(numelements= 1000, maptype ='CHAINING',  
                                      comparefunction=compareStopIds)
        return analyzer
        
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')


# Funciones para agregar informacion al catalogo

def addTransbordotoTabla(analyzer, llave, nombre_bus):
    concatenacion = "T-" + llave
    este = m.contains(analyzer['transbordos'],concatenacion)
    if este == False:
        m.put(analyzer['transbordos'],concatenacion, [nombre_bus])
    else: 
        entry = m.get(analyzer['transbordos'],concatenacion)
        lista = me.getValue(entry)
        lista.append(nombre_bus)
        m.put(analyzer['transbordos'],concatenacion, lista)
    return este
        
           #en esta tabla se almacenen los buses asociados a cada transbordo
def tablitaInfo (analyzer,llave,stop):
    valor = {'Bus_Stop':stop["Bus_Stop"],'Transbordo':stop['Transbordo'], 'Longitude':stop['Longitude'], 'Latitude': stop['Latitude'], 'Distric_Name':stop['District_Name'], 'Neighborhood':stop['Neighborhood_Name']}
    m.put(analyzer['vertices'],llave, valor)
    
def calcular_peso(analyzer, inicio, fin, lat_max, lat_min, long_max, long_min):
    entry_inicio = m.get(analyzer['vertices'],inicio )
    entry_fin = m.get(analyzer['vertices'],fin)
    valor = me.getValue(entry_inicio)
    valorFin = me.getValue(entry_fin)
    longitud_inicio = valor["Longitude"]
    longitud_inicio = float(longitud_inicio)
    latitud_inicio = valor["Latitude"]
    latitud_inicio = float(latitud_inicio)
    longitud_fin = valorFin["Longitude"]
    longitud_fin = float(longitud_fin)
    latitud_fin = valorFin["Latitude"]
    latitud_fin = float(latitud_fin)

    peso = haversine(longitud_inicio,latitud_inicio,longitud_fin,latitud_fin)
    lat_max_n, lat_min_n, long_max_n, long_min_n = actualizar_long_lat(lat_max, lat_min, long_max, long_min, longitud_inicio, latitud_inicio, longitud_fin, latitud_fin)
    return lat_max_n, lat_min_n, long_max_n, long_min_n, peso


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

def unirTransbordos(analyzer):
    llaves_transbordos = m.keySet(analyzer["transbordos"])   #estas son de la forma T-numero
    #print(llaves_transbordos)
    for llave in range(lt.size(llaves_transbordos)):
        entry = m.get(analyzer['transbordos'],lt.getElement(llaves_transbordos,llave+1))
        lista_buses = me.getValue(entry)
        gr.insertVertex( analyzer['grafo'], me.getKey(entry))  #agrego nodo de transbordo
        llave_limpia = me.getKey(entry)[2:] # le quito el T- a la llave
        for bus in lista_buses:
            concatenacion = llave_limpia + '-' + bus
            #que onda con estos buses estaticos
            if concatenacion != "1638-L46" and concatenacion != "1638-L52":
                gr.addEdge(analyzer['grafo'], me.getKey(entry), concatenacion, 0 )  
                gr.addEdge(analyzer['grafo'], concatenacion,me.getKey(entry), 0 )
        


def crearBosque(analyzer, inicio, fin,peso):
    if gr.containsVertex(analyzer['grafo'], inicio) == False:
        gr.insertVertex(analyzer['grafo'], inicio)
    if gr.containsVertex(analyzer['grafo'], fin) == False:
        gr.insertVertex(analyzer['grafo'], fin)
    gr.addEdge(analyzer['grafo'], inicio, fin,peso )

   
def primerasyultimas5(analyzer):
    primeras=lt.newList('SINGLE_LINKED')
    ultimas=lt.newList('SINGLE_LINKED')
    adj_p = lt.newList('SINGLE_LINKED')
    adj_u = lt.newList('SINGLE_LINKED')
    lista2=m.keySet(analyzer['vertices'])
    merge.sort(lista2, compareestaciones2)
    i=0
    tamano=lt.size(lista2)
    while i<5:
        estacionp=m.get(analyzer['vertices'],lt.getElement(lista2,i+1))
        estacionu=m.get(analyzer['vertices'],lt.getElement(lista2,tamano-i))
        lt.addLast(primeras, estacionp)
        lt.addLast(ultimas, estacionu)
        lt.addLast(adj_p, gr.outdegree(analyzer['grafo'],lt.getElement(lista2,i+1)))
        lt.addLast(adj_u, gr.outdegree(analyzer['grafo'],lt.getElement(lista2,tamano-i)))
        i += 1
    return(primeras, ultimas, adj_p, adj_u)  

# Funciones de consulta

#req 1

def existsPath(analyzer, station1, station2):
    analyzer["posibles"] = None
    analyzer["posibles"] = dfs.DepthFirstSearch(analyzer['grafo'],station1)
    salida = dfs.pathTo(analyzer['posibles'], station2)
    lista_lat_long = []
    lista_identificadores = []
    lista_distancias = []
    total_transbordos = 0
    distancia_total = 0
    if salida != None:
        lista_identificadores, lista_distancias, total_transbordos, distancia_total, lista_lat_long = recorrido(salida, analyzer, station1, station2)    
    return salida, lista_identificadores, lista_distancias, total_transbordos, distancia_total, lista_lat_long

#req 2
def shortestPath(analyzer, station1, station2):
    analyzer["cortos_saltos"] = None
    analyzer["cortos_saltos"] = bfs.BreadhtFisrtSearch(analyzer['grafo'],station1)
    salida = bfs.pathTo(analyzer['cortos_saltos'], station2)
    lista_lat_long = []
    lista_identificadores = []
    lista_distancias = []
    total_transbordos = 0
    distancia_total = 0
    if salida != None:
        lista_identificadores, lista_distancias, total_transbordos, distancia_total, lista_lat_long = recorrido(salida, analyzer, station1, station2)
    return salida, lista_identificadores, lista_distancias, total_transbordos, distancia_total, lista_lat_long

def recorrido(salida, analyzer, station1, station2):
    lista_lat_long = []
    lista_identificadores = []
    lista_distancias = []
    total_transbordos = 0
    actual = station1
    long1, lat1 = me.getValue(m.get(analyzer['vertices'],actual))["Longitude"], me.getValue(m.get(analyzer['vertices'],actual))["Latitude"] 
    distancia_total = 0
    stk.pop(salida)
    for i in range(stk.size(salida)):
        distancia = 0
        siguiente = stk.pop(salida)
        if "T-" in actual:
            total_transbordos += 1
            distancia = 0
            lista_identificadores.append(actual)
            lista_distancias.append(distancia)
            lista_lat_long.append([lat1, long1])
            actual = siguiente       
        elif "T-" in siguiente:
            distancia = 0
            lista_identificadores.append(actual)
            lista_distancias.append(distancia)
            long1, lat1 = me.getValue(m.get(analyzer['vertices'],actual))["Longitude"], me.getValue(m.get(analyzer['vertices'],actual))["Latitude"] 
            lista_lat_long.append([lat1, long1])
            actual = siguiente       
        else:
            long1, lat1 = me.getValue(m.get(analyzer['vertices'],actual))["Longitude"], me.getValue(m.get(analyzer['vertices'],actual))["Latitude"] 
            long2, lat2 = me.getValue(m.get(analyzer['vertices'],siguiente))["Longitude"], me.getValue(m.get(analyzer['vertices'],siguiente))["Latitude"] 
            lista_lat_long.append([lat1, long1])
            distancia = haversine(float(long1), float(lat1), float(long2), float(lat2))
            lista_identificadores.append(actual)
            actual = siguiente
            lista_distancias.append(distancia)
            distancia_total += distancia
        
    lista_identificadores.append(station2)
    lista_distancias.append(0)
    lista_lat_long.append([me.getValue(m.get(analyzer['vertices'],station2))["Latitude"],me.getValue(m.get(analyzer['vertices'],station2))["Longitude"] ])
    
    return lista_identificadores, lista_distancias, total_transbordos, distancia_total, lista_lat_long

#requ 3 
def Fconectados(analyzer): 

    kosaraju = scc.KosarajuSCC(analyzer['grafo']) # se implementa cosaraju que me saca un diccionario con llaves components y idscc (que usasre) 
    total = kosaraju['components'] #me da el total de componentes conectados
    
    componentes = om.newMap(comparefunction = cmpNumero) 
    i = 1
    while i <= total: # este while va a ser usado con el proposito de crear un diccionario que me diga cauntos conectados por cada componente, se modifico scc para funcionar mas rapido


        actual = kosaraju[str(i)] # esto esta sacando del scc unos componentes nuevos que se crearon, donde dice el valor de cada uno 

        om.put(componentes,str(actual),str(i))
        i +=1
    
    identificadores = {  # en este se sacan los priemros 3 y ultimos tres identificadores de todas las componentes
    }
    llaves = m.keySet(kosaraju['idscc']) # esto devuelve todos los identificadores
    mapacho = m.newMap(numelements= 1000, maptype ='CHAINING') 
                                    
    tamano = lt.size(llaves) 
    
    for x in range(1,tamano+1): 
        llave = lt.getElement(llaves,x) 
        entry = m.get(kosaraju['idscc'],llave) # saca la pareja llave valor  de la posicion x de la lista de identificadores

        mapComponente = me.getValue(entry) # valor seria el componente al cual pertenece

        mapIdentificador = me.getKey(entry)# llave seria el identificador

        if m.contains(mapacho,entry['value']):
            pareja = m.get(mapacho,mapComponente)
            lista = me.getValue(pareja)
            lt.addLast(lista,mapIdentificador)
        else:
            lista =lt.newList()
            lt.addLast(lista,mapIdentificador)
            m.put(mapacho,mapComponente,lista)
    for comp in range(1,total+1):
        parejaX = m.get(mapacho,comp)
        listaX = me.getValue(parejaX)
        # print('ESTA ES de '+str(comp))
        merge.sort(listaX,cmpIDSSS)
        identificadores[str(comp)]=lt.newList()
        grado = lt.size(listaX)
        # if grado == 6:
        #     print(listaX)
        for k in range(0,3):
            mapllave = lt.getElement(listaX,k+1)
            lt.addFirst(identificadores[str(comp)],mapllave)
            ultimo = lt.getElement(listaX,grado-k)
            lt.addLast(identificadores[str(comp)],ultimo)
    # print('identificador 1 '+ str(identificadores['1']))
    # print('identificador 2 '+ str(identificadores['2']))
    # print('identificador 3 '+ str(identificadores['3']))
    # print('identificador 4 '+ str(identificadores['4']))
    # print('identificador 5 '+ str(identificadores['5']))
    # print('identificador 6 '+ str(identificadores['6']))
    return  total, componentes,identificadores
#req 4 

def distanciaGeografica(copia_tabla,analyzer,long1, lat1, long2, lat2, prohibidas):
    analyzer["cortos_peso"] = None
    distancia_origen, estacion_origen, distancia_destino, estacion_destino = actualizar_distancia(copia_tabla, long1, lat1, long2, lat2, prohibidas) 
    estacion_origen_original = estacion_origen #estas se usan para obtener la longitud y latitud por si son de transbordo
    estacion_destino_original = estacion_destino
    posicion_raya1 = estacion_origen.rfind("-")
    posicion_raya2 = estacion_destino.rfind("-")
    if m.contains(analyzer["transbordos"],"T-" + estacion_origen[:posicion_raya1]):
        estacion_origen = "T-" + estacion_origen[:posicion_raya1]
    if m.contains(analyzer["transbordos"],"T-" + estacion_destino[:posicion_raya2]):
        estacion_destino = "T-" + estacion_destino[:posicion_raya2]
    analyzer["cortos_peso"] = djk.Dijkstra(analyzer['grafo'], estacion_origen)
    try: 
        hay_camino = djk.hasPathTo(analyzer["cortos_peso"], estacion_destino) 
    except:
        hay_camino = False

    if hay_camino:
        distancia_vertices = djk.distTo(analyzer["cortos_peso"], estacion_destino)
        camino = djk.pathTo(analyzer['cortos_peso'], estacion_destino)
        lista_identificadores = []
        lista_distancias = []
        total_transbordos = 0
        lista_long_lat = []
        actual = estacion_origen_original
        for i in range(stk.size(camino)):
            distancia = 0
            siguiente = stk.pop(camino)["vertexA"]
            if "T-" in siguiente:
                total_transbordos += 1
            if "T-" not in siguiente and "T-" not in actual:  
                long1, lat1 = me.getValue(m.get(analyzer['vertices'],actual))["Longitude"], me.getValue(m.get(analyzer['vertices'],actual))["Latitude"] 
                long2, lat2 = me.getValue(m.get(analyzer['vertices'],siguiente))["Longitude"], me.getValue(m.get(analyzer['vertices'],siguiente))["Latitude"] 
                distancia = haversine(float(long1), float(lat1), float(long2), float(lat2))
                lista_long_lat.append([lat1, long1])
            elif "T-" not in actual:
                long1, lat1 = me.getValue(m.get(analyzer['vertices'],actual))["Longitude"], me.getValue(m.get(analyzer['vertices'],actual))["Latitude"] 
                lista_long_lat.append([lat1, long1]) 
                distancia = 0
            else: 
                lista_long_lat.append([lat1, long1]) 
                distancia = 0
            lista_identificadores.append(actual)
            actual = siguiente    
            lista_distancias.append(distancia)
    else:
        print("El primer camino obtenido no es posible, calculando otro camino...")
        prohibidas.append(estacion_destino)
        distanciaGeografica(analyzer,long1, lat1, long2, lat2, prohibidas)
    
    lista_identificadores.append(estacion_destino)
    lista_distancias.append(0)
    lista_long_lat.append([me.getValue(m.get(analyzer['vertices'],estacion_destino_original))["Latitude"],me.getValue(m.get(analyzer['vertices'],estacion_destino_original))["Longitude"] ])
    
    return distancia_origen, distancia_vertices, distancia_destino, lista_identificadores, lista_distancias, total_transbordos,lista_long_lat

def actualizar_distancia(copia_tabla, long1, lat1, long2, lat2, prohibidas):
    for prohibida in prohibidas:
        m.remove(copia_tabla, prohibida)
    distancia_menor_origen = float('inf')
    distancia_menor_destino = float('inf')
    estacion_cercana_origen = ""
    estacion_cercana_destino = ""
    llaves = m.keySet(copia_tabla)
    for i in range(lt.size(llaves)):
        entry = m.get(copia_tabla, lt.getElement(llaves,i))
        long_act, lat_act = me.getValue(entry)["Longitude"], me.getValue(entry)["Latitude"]
        distancia_origen = haversine(float(long_act), float(lat_act), long1, lat1)
        distancia_destino = haversine(float(long_act), float(lat_act), long2, lat2)
        if distancia_origen < distancia_menor_origen:
            distancia_menor_origen = distancia_origen
            estacion_cercana_origen = me.getKey(entry)
        if distancia_destino < distancia_menor_destino:
            distancia_menor_destino = distancia_destino
            estacion_cercana_destino = me.getKey(entry)
    
    return distancia_menor_origen, estacion_cercana_origen, distancia_menor_destino, estacion_cercana_destino


#req 5 
def estacionesAlcanzables(analyzer, origen, maxestaciones):
    partida=djk.Dijkstra(analyzer['grafo'],origen)
    todas_estaciones_alcanzables=lt.newList()
    estaciones_requeridas=[]
    lista_lat_long = []
    conexiones=[]
    distancias=[]
    lista=m.keySet(analyzer['vertices'])
    for vertice in lt.iterator(lista):
        if djk.hasPathTo(partida, vertice) ==True:
            lt.addLast(todas_estaciones_alcanzables, vertice)
    print('las estaciones model')
    print(lt.size(todas_estaciones_alcanzables))
    for vertice in lt.iterator(todas_estaciones_alcanzables):
        if lt.size(djk.pathTo(partida, vertice))<=maxestaciones:
            estaciones_requeridas.append(vertice)
            conexiones.append(lt.size(djk.pathTo(partida, vertice)))
            # lt.addLast(estaciones_requeridas, vertice)
            # lt.addLast(conexiones, lt.size(djk.pathTo(partida, vertice)))
            info=me.getValue(m.get(analyzer['vertices'],vertice))
            long1, lat1 = me.getValue(m.get(analyzer['vertices'],origen))["Longitude"], me.getValue(m.get(analyzer['vertices'],origen))["Latitude"] 
            long2, lat2 = info["Longitude"], info["Latitude"] 
            distancia = haversine(float(long1), float(lat1), float(long2), float(lat2))
            lista_lat_long.append([info["Latitude"], info["Longitude"]])
            distancias.append(distancia)
            # lt.addLast(latitudes, info["Latitude"] )
            # lt.addLast(longitudes, info["Longitude"] )
        else:
            pass
    print(estaciones_requeridas)
    print(lista_lat_long)
    print(conexiones)
    return estaciones_requeridas, lista_lat_long,conexiones,distancias

#bla bla

#req 6 
def distanciaVecindario(analyzer, origen, vecindario):
    return None

#vamos a hacer un mapa  
#req 6 ana

def addVecindarioStation(analyzer,  contenido):
    vecindarios = analyzer['vecindarios']
    vecindario = contenido["Neighborhood_Name"]
    existvecindad = m.contains(vecindarios, vecindario)
    if existvecindad:
        entry = m.get(vecindarios, vecindario)
        vec = me.getValue(entry)
    else:
        vec = nuevoVecindario(vecindario)
        m.put(vecindarios, vecindario, vec)
    lt.addLast(vec['lista'], contenido)

def nuevoVecindario(vecindario): 
    entry = {'vecindario': None , "lista": None}
    entry['vecindario'] = vecindario
    entry['lista'] = lt.newList("SINGLE_LINKED", compareestaciones2)
    return entry

def distminestacion_vecindario(analyzer, estacion, vecindario):
    #1.vamos a crear un mapa de vecindarios
    #2. vamos a quedarnos con la casilla de ese vecindario
    search= m.get(analyzer['vecindarios'], vecindario)['value']['lista']
    #3. vamos a evaluar las distancias desde mi estacion hasta esa casilla. Cogemos el camino mas corto de esos
    camino=None
    camino_duracion=0
    partida=djk.Dijkstra(analyzer['grafo'],estacion)
    #partida=djk.Dijkstra(analyzer['grafo'],estacion)
    for x in lt.iterator(search):
        bus_stop = x["Bus_Stop"].split('-')
        bus_stop = bus_stop[1].strip(' ')
        station = x["Code"] + '-' + bus_stop 
        #arco=gr.getEdge(analyzer['grafo'], estacion, station)
        camino_evaluado=djk.pathTo(partida, station)
        lon1 = me.getValue(m.get(analyzer['vertices'],estacion))["Longitude"]
        lat1= me.getValue(m.get(analyzer['vertices'],estacion))["Latitude"]
        lon2 = me.getValue(m.get(analyzer['vertices'],station ))["Longitude"]
        lat2=  me.getValue(m.get(analyzer['vertices'],station ))["Longitude"]
        arco_duracion= haversine(float(lon1), float(lat1), float(lon2), float(lat2))
        if camino==None:
            camino = camino_evaluado
            camino_duracion = arco_duracion
        elif arco_duracion<camino_duracion:
            camino = camino_evaluado
            camino_duracion = arco_duracion 
        else:
            pass
        #4.ahora que ya obtuvimos el camino sacamos los datos que necesitamos
        
    lista_identificadores = []
    lista_distancias = []
    total_transbordos = 0
    distancia_total=0
    vecindarios=[]
    lista_lat_long = []
    #stk.pop(camino)
    for i in range(stk.size(camino)):
        out_pop = stk.pop(camino)
        info=m.get(analyzer['vertices'], out_pop["vertexA"])
        print(info)
        if "T-" in out_pop["vertexA"]:
            total_transbordos += 1
        elif "T-" not in out_pop["vertexA"] and "T-" not in out_pop["vertexB"]:
            lista_identificadores.append(out_pop["vertexA"])
            lista_distancias.append(out_pop['weight']) 
            vecindarios.append(info['value']["Neighborhood"]) 
            lista_lat_long.append([info['value']["Latitude"],info['value']["Longitude"]])
            distancia_total += out_pop['weight']
        #else:
            #distancia = out_pop['weight']
        else:
            pass
        #anterior = out_pop["vertexA"]
    #print(camino)
    #print(lista_distancias)
    #print(lista_identificadores)
    #print(vecindarios)  
    #print(latitudes)     
    return camino, lista_identificadores, lista_distancias, total_transbordos, distancia_total,vecindarios, lista_lat_long
    
    

    #req 7

  
  
def circular(analyzer, start_node):
    graph = analyzer['grafo']
    # m = dfs.DepthFirstSearch(graph['grafo'],start_node)
    # print(str(m['ciclo'] ))
    # lista = gr.adjacents(graph['grafo'], '279-81')
    # print (str(lt.isPresent(lista,'T-278')))

    # print('ENTRA')
    # m['visited']
    k = cycles.DirectedCycle(graph)
    search = cycles.initStructures(graph)
    cycles.dfs(graph, search, start_node)
    ciclo = cycles.cycle(search)
    informacio = ciclo['last']['info']
    distancia = 0
    estaciones = 0
    transbordos = 0
    camino = None
    # print(str(ciclo))
    eto = gr.adjacents(graph,start_node)
    # print(str(eto))
    estaciones = stk.size(ciclo)
    # print('ESTACIONES')
    # print(str(estaciones))
    camino = lt.newList()
    for ooi in range(stk.size(ciclo)):

        elemento = stk.pop(ciclo)        
        # print('elemento'+str(elemento))
        if 'T' in elemento['vertexA']:
            transbordos += 1
        if 'T' in elemento['vertexB']:
            transbordos += 1
        distancia += elemento['weight']
        # print('1ONE')
        tupla = [elemento['vertexA'],elemento['vertexB'],elemento['weight']]
        lt.addLast(camino,tupla)
        

    return distancia,estaciones,transbordos,camino
     


        
# Funciones para creacion de datos

# Funciones de consulta

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento

def actualizar_long_lat(lat_max, lat_min, long_max, long_min, long_inicio, lat_inicio, long_fin, lat_fin):
    if lat_inicio > lat_max:
        lat_max = lat_inicio

    elif lat_inicio < lat_min:
        lat_min = lat_inicio

    if long_inicio > long_max:
        long_max = long_inicio

    elif long_inicio < long_min:
        long_min = long_inicio

    if lat_fin > lat_max:
        lat_max = lat_fin

    elif lat_fin < lat_min:
        lat_min = lat_fin

    if long_fin > long_max:
        long_max = long_fin

    elif long_fin < long_min:
        long_min = long_fin  
    return lat_max, lat_min, long_max, long_min

def areaRectangular():
    lista = [long_min, long_max, lat_min, lat_max]
    #print(lista)
    return lista

def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['grafo'])


# Funciones utilizadas para comparar elementos dentro de una lista

def compareStopIds(vertice, keyvaluevertice):
    """
    Compara dos estaciones
    """
    verticecode = keyvaluevertice['key']
    if (vertice == verticecode):
        return 0
    elif (vertice > verticecode):
        return 1
    else:
        return -1
def compareestaciones(dato1, dato2):

    if (dato1['Bus_Stop']) > (dato2['Bus_Stop']):
            return True
    elif (dato1['Bus_Stop']) < (dato2['Bus_Stop']):
        return False

def compareestaciones2(dato1, dato2):
    parte1_1 = dato1.split("-")[0]
    parte2_1 = dato1.split("-")[1]
    parte1_2 = dato2.split("-")[0]
    parte2_2 = dato2.split("-")[1]
    
    if int(parte1_1) > int(parte1_2):
        return False
    elif int(parte1_1) < int(parte1_2):
        return True
    else:
        if str(parte2_1) > str(parte2_2):
            return False
        elif str(parte2_1) < str(parte2_2):
            return True

def crear_mapa(lista_long_lat, lista_identificadores, req):
    if req == 5:
        my_map=folium.Map(location=[41.39465,2.138794])
        for i in range(len(lista_long_lat)):
            folium.Marker(lista_long_lat[i], popup = str(lista_identificadores[i]), icon=folium.Icon(color="blue")).add_to(my_map)
    else:
        my_map=folium.Map(location=[41.39465,2.138794])
        lista_agregados = []
        importante = False
        for i in range(len(lista_long_lat)):
            if i == 0:
                folium.Marker(lista_long_lat[i], popup = "Origen: " + str(lista_identificadores[i]) , icon=folium.Icon(color="green")).add_to(my_map)    
                lista_agregados.append(lista_long_lat[i])
                importante = True
            elif i == len(lista_long_lat) -1:
                folium.Marker(lista_long_lat[i], popup = "Destino : " + str(lista_identificadores[i]), icon=folium.Icon(color="red")).add_to(my_map)
                lista_agregados.append(lista_long_lat[i])
                importante = True
                    
            if lista_long_lat[i] in lista_agregados:
                if "T-" in lista_identificadores[i] and importante == False:
                    folium.Marker(lista_long_lat[i], popup = str(lista_identificadores[i]) , icon=folium.Icon(color="orange")).add_to(my_map)    
            else:
                folium.Marker(lista_long_lat[i], popup = str(i) + ": " + str(lista_identificadores[i]), icon=folium.Icon(color="blue")).add_to(my_map)
                lista_agregados.append(lista_long_lat[i])
                importante = False

    my_map.save("map.html")
    webbrowser.open("map.html")



def cmpIDSSS(dato1,dato2):
    dato1 = dato1.split('-')
    dato2 = dato2.split('-')
    # print('DATOS')
    # print(str(dato1))
    # print(str(dato2))
    if  ('T' in dato1[0])and ('T' in dato2[0]):
        # print('AMBOS T')
        if (int(dato1[1]) > int(dato2[1])):
            # print('MAYOR EL 1 ')
            # print(str(dato1))
            # print(str(dato2))
            return -1
        elif (int(dato1[1]) < int(dato2[1])):
            # print('MENOR EL 1 ')
            # print(str(dato1))
            # print(str(dato2))
            return 1
    elif ('T' in dato1[0]):
        # print('tiene T el 1 por lo que 1 menor')
        # print(str(dato1))
        # print(str(dato2))
        return 1
    elif ('T' in dato2[0]):
        # print('tiene T el 2 por lo que 1 mayor')
        # print(str(dato1))
        # print(str(dato2))
        return -1
    elif (int(dato1[0]) == int(dato2[0])):
        # print('IGUALES')
        if (dato1[1] > dato2[1]):
            # print('MAYOR EL 1 ')
            # print(str(dato1))
            # print(str(dato2))
            return -1
        elif (dato1[1] < dato2[1]):
            # print('MENOR EL 1 ')
            # print(str(dato1))
            # print(str(dato2))
            return 1
        else:
            return 0
    elif (int(dato1[0]) > int(dato2[0])):
        # print('MAYOR EL 1')
        # print(str(dato1))
        # print(str(dato2))
        return -1
    elif (int(dato1[0]) < int(dato2[0])):
        # print('MENOR EL 1')
        # print(str(dato1))
        # print(str(dato2))
        return 1
def cmpNumero(a, b):
    """
    Compara dos numeors
    """
    a =int(a)
    b = int(b)
    if (a == b):
        return 0
    elif (a > b):
        return -1
    else:
        return 1