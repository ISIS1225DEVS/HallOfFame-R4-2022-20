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
 Siuu
 """


from csv import list_dialects
import config as cf
import time
import networkx as nx
import graphviz
import matplotlib.pyplot as plt
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import orderedmap as om
from DISClib.ADT import graph as gr
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import dfs
from DISClib.Algorithms.Graphs import bfs
from DISClib.Algorithms.Graphs import cycles as cy
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Algorithms.Sorting import mergesort as mer
from DISClib.Utils import error as error
from math import radians, cos, sin, asin, sqrt
assert cf


"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos



def newCatalog():

    
    try:
        

        catalog = {
            'connections': None,
            'components': None,
            'paths': None,
            'search': None,
        }
        catalog['G'] = nx.Graph()
        catalog['vertices']=lt.newList('ARRAY_LIST',None)
        catalog['transbordo']=lt.newList('ARRAY_LIST',None)
        catalog['arcos']=lt.newList('ARRAY_LIST',None)

        catalog['stops'] = mp.newMap(numelements=140,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        catalog['grafo'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareStopIds)
        return catalog
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al catalogo

def addVertice(analyzer, vertice):
    lt.addLast(analyzer["vertices"], vertice)

    mp.put(analyzer['stops'],formatVertex(vertice),vertice)
    if vertice['Transbordo']=='S':
        lt.addLast(analyzer['transbordo'],vertice)

    
    addStop(analyzer, formatVertex(vertice))
    return analyzer

def addArco(analyzer, arco):
    lt.addLast(analyzer["arcos"], arco)
    stop1=arco['Code']+'-'+arco['Bus_Stop'][4:]
    stop2=arco['Code_Destiny']+'-'+arco['Bus_Stop'][4:]

    mapa=analyzer['stops']

    vertex1=mp.get(mapa,stop1)
    vertex1=me.getValue(vertex1)
    vertex1=[float(vertex1['Longitude']),float(vertex1['Latitude'])]
        
    vertex2=mp.get(mapa,stop2)
    vertex2=me.getValue(vertex2)
    vertex2=[float(vertex2['Longitude']),float(vertex2['Latitude'])]
    dist=haversine(vertex1[0],vertex1[1],vertex2[0],vertex2[1])
    addConnection(analyzer,stop1,stop2,dist)
    return analyzer

def addTransbordo(analyzer):
    cont=0
    for i in lt.iterator(analyzer['transbordo']):
        vertex='T-'+i['Code']
        vertex2=formatVertex(i)
        if gr.containsVertex(analyzer['grafo'],vertex):
            addConnection(analyzer,vertex,vertex2,0)
            addConnection(analyzer,vertex2,vertex,0)
        else:
            addStop(analyzer,vertex)
            addConnection(analyzer,vertex,vertex2,0)
            addConnection(analyzer,vertex2,vertex,0)
            cont+=1
    
    #nx.draw_networkx(analyzer['G'])
    #plt.show()

    return cont

def addStop(analyzer, stopid):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['grafo'], stopid):
            analyzer['G'].add_node(stopid)
            gr.insertVertex(analyzer['grafo'], stopid)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addstop')

def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['grafo'], origin, destination)
    if edge is None:
        analyzer['G'].add_edge(origin, destination)
        gr.addEdge(analyzer['grafo'], origin, destination, distance)
    return analyzer



# Funciones de consulta

def totalStops(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['grafo'])

def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['grafo'])


def getReq1(analyzer,ini,dest):
    start_time=getTime()
    G=nx.Graph()
    cont_trans=0
    dist_total=0
    dict_edges={}
    analyzer["search"]=dfs.DepthFirstSearch(analyzer["grafo"], ini)
    exist= dfs.hasPathTo(analyzer['search'], dest)
    path_new=lt.newList('ARRAY_LIST')
    if exist:
        path= dfs.pathTo(analyzer['search'],dest)

        for i in range(1,lt.size(path)):
            if not G.has_node(lt.getElement(path,i)):
                G.add_node(lt.getElement(path,i))
                G.add_node(lt.getElement(path,i+1))
            else:
                G.add_node(lt.getElement(path,i+1))
            
            if 'T-' in lt.getElement(path,i):
                cont_trans+=1

            dist=gr.getEdge(analyzer['grafo'],lt.getElement(path,i),lt.getElement(path,i+1))['weight']
            dict_edges[(lt.getElement(path,i),lt.getElement(path,i+1))]=round(dist,2)
            G.add_edge(lt.getElement(path,i),lt.getElement(path,i+1))
            dist_total+=dist
            lt.addFirst(path_new,[lt.getElement(path,i+1),dist])
        lt.addLast(path_new,[lt.getElement(path,1),0])
        end_time=getTime()
        times=deltaTime(start_time,end_time)
        
        return True, dist_total, lt.size(path), cont_trans, path_new,G,dict_edges,round(times,3)
    else:
        end_time=getTime()
        times=deltaTime(start_time,end_time)
        return False,0, 0, 0, 0,0,0,round(times,3)

def getReq2 (analyzer,ini,dest):
    start_time=getTime()
    G=nx.Graph()
    cont_trans=0
    dist_total=0
    dict_edges={}
    analyzer["search"]=bfs.BreadhtFisrtSearch(analyzer["grafo"], ini)
    exist= bfs.hasPathTo(analyzer['search'], dest)
    path_new=lt.newList('ARRAY_LIST')
    if exist:
        path= bfs.pathTo(analyzer['search'],dest)

        for i in range(1,lt.size(path)):
            if not G.has_node(lt.getElement(path,i)):
                G.add_node(lt.getElement(path,i))
                G.add_node(lt.getElement(path,i+1))
            else:
                G.add_node(lt.getElement(path,i+1))
            
            if 'T-' in lt.getElement(path,i):
                cont_trans+=1

            dist=gr.getEdge(analyzer['grafo'],lt.getElement(path,i),lt.getElement(path,i+1))['weight']
            dict_edges[(lt.getElement(path,i),lt.getElement(path,i+1))]=round(dist,2)
            G.add_edge(lt.getElement(path,i),lt.getElement(path,i+1))
            dist_total+=dist
            lt.addFirst(path_new,[lt.getElement(path,i+1),dist])
        lt.addLast(path_new,[lt.getElement(path,1),0])
        end_time=getTime()
        times=deltaTime(start_time,end_time)
        
        return True, dist_total, lt.size(path), cont_trans, path_new,G,dict_edges,round(times,3)
    else:
        end_time=getTime()
        times=deltaTime(start_time,end_time)
        return False,0, 0, 0, 0,0,0,round(times,3)

def getReq3(analyzer):
    start_time=getTime()
    analyzer['components'] = scc.KosarajuSCC(analyzer['grafo'])
    cant_conectados=scc.connectedComponents(analyzer['components'])

    mapa_vertices= analyzer['components']['idscc']
    mapa_componentes={}
    for i in lt.iterator(analyzer['vertices']):
        try:
            componente=mp.get(mapa_vertices,formatVertex(i))
            componente=me.getValue(componente)
            
            if componente in mapa_componentes:
                lista_vertex=mapa_componentes[componente]
            else:
                lista_vertex={'lista_vertex':lt.newList('ARRAY_LIST'), 'count':0}
                mapa_componentes[componente]=lista_vertex
            lt.addLast(lista_vertex['lista_vertex'],formatVertex(i))
            lista_vertex['count']+=1
        except:
            pass
    
    for i in mapa_componentes:
        mer.sort(mapa_componentes[i]['lista_vertex'],cmpByCode)
       
    mapa_componentes=sorted(mapa_componentes.items(), key=lambda x:x[1]['count'], reverse=True)
    mapa_componentes=dict(mapa_componentes)
    
    end_time=getTime()
    times=deltaTime(start_time,end_time)

    return cant_conectados, mapa_componentes,round(times,3)

def getReq4(analyzer,lon_ini,lat_ini, lon_dest,lat_dest):
    start_time=getTime()
    G=nx.Graph()
    cont_trans=0
    dist_total=0
    dict_edges={}
    
    ini=''
    dist_menor_ini=9999999999
    for i in lt.iterator(analyzer['vertices']):
        dist_est=haversine(lon_ini,lat_ini,float(i['Longitude']),float(i['Latitude']))
        if dist_est<dist_menor_ini:
            dist_menor_ini=dist_est
            ini=formatVertex(i)
        if dist_menor_ini==0:
            break
    
    dest=''
    dist_menor_dest=999999999
    for i in lt.iterator(analyzer['vertices']):
        dist_est=haversine(lon_dest,lat_dest,float(i['Longitude']),float(i['Latitude']))
        if dist_est<dist_menor_dest:
            dist_menor_dest=dist_est
            dest=formatVertex(i)
        if dist_menor_dest==0:
            break
    
    analyzer['search']=djk.Dijkstra(analyzer['grafo'],ini)
    exist= djk.hasPathTo(analyzer['search'], dest)
    path_new=lt.newList('ARRAY_LIST')
    if exist:
        path= djk.pathTo(analyzer['search'],dest)

        for i in range(1,lt.size(path)+1):
            if not G.has_node(lt.getElement(path,i)['vertexA']):
                G.add_node(lt.getElement(path,i)['vertexA'])
                G.add_node(lt.getElement(path,i)['vertexB'])
            else:
                G.add_node(lt.getElement(path,i)['vertexB'])
            
            if 'T-' in lt.getElement(path,i)['vertexA']:
                cont_trans+=1

            dist=gr.getEdge(analyzer['grafo'],lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])['weight']
            dict_edges[(lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])]=round(dist,2)
            G.add_edge(lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])
            dist_total+=dist
            lt.addFirst(path_new,[lt.getElement(path,i)['vertexA'],dist])
        lt.addLast(path_new,[lt.getElement(path,0)['vertexB'],0])

        end_time=getTime()
        times=deltaTime(start_time,end_time)
        
        return True, dist_menor_ini, dist_total, dist_menor_dest, lt.size(path_new), cont_trans, path_new,G,dict_edges,round(times,3)
    else:
        end_time=getTime()
        times=deltaTime(start_time,end_time)
        return False,0, 0, 0, 0,0,0,0,0,round(times,3)

def getReq5(analyzer,ini,num):
    start_time=getTime()
    G=nx.Graph()
    
    analyzer['search']=djk.Dijkstra(analyzer['grafo'],ini)
    
    lst_adj=gr.adjacents(analyzer['grafo'],ini)
    lst_new=lt.newList('ARRAY_LIST')

    info=mp.get(analyzer['stops'],ini)
    info=me.getValue(info)
    lt.addLast(lst_new,[ini,info['Longitude'],info['Latitude'],0])
    for i in lt.iterator(lst_adj):
        if 'T-' not in i:
            info=mp.get(analyzer['stops'],i)
            info=me.getValue(info)
            lt.addLast(lst_new,[i,info['Longitude'],info['Latitude'],djk.distTo(analyzer['search'],i)])
            G.add_node(i)
        else:
            lt.addLast(lst_new,[i,'transbordo','transbordo',0])
            G.add_node(i)
        if i!=ini:
            G.add_edge(ini,i)

    if num>0:
        for i in range(1,num+1):
            nuevo_ini=lt.getElement(lst_new,i)[0]
            lst_adj_new=gr.adjacents(analyzer['grafo'],nuevo_ini)
            
            for j in lt.iterator(lst_adj_new):
                if 'T-' not in j:
                    info=mp.get(analyzer['stops'],j)
                    info=me.getValue(info)
                    if lt.isPresent(lst_new,[j,info['Longitude'],info['Latitude'],djk.distTo(analyzer['search'],j)])==0:
                        G.add_node(j)
                        lt.addLast(lst_new, [j,info['Longitude'],info['Latitude'],djk.distTo(analyzer['search'],j)])
                else:
                    if lt.isPresent(lst_new,[j,'transbordo','transbordo',0])==0:
                        G.add_node(j)
                        lt.addLast(lst_new, [j,'transbordo','transbordo',0])
                G.add_edge(nuevo_ini,j)
    end_time=getTime()
    times=deltaTime(start_time,end_time)
    
    return lst_new,G,round(times,3)

def getReq6(analyzer,ini,barrio):
    start_time=getTime()
    G=nx.Graph()
    cont_trans=0
    dist_total=0
    dict_edges={}
    
    lista_barrio=lt.newList('ARRAY_LIST')
    for i in lt.iterator(analyzer['vertices']):
        if barrio in i['Neighborhood_Name']:
            lt.addLast(lista_barrio,i)

    path=lt.newList('ARRAY_LIST')
    try:
        analyzer['search']=djk.Dijkstra(analyzer['grafo'],ini)

    
        dist_menor_dest=999999999
        for i in lt.iterator(lista_barrio):
            exist= djk.hasPathTo(analyzer['search'], formatVertex(i))
            if exist:
                path_probable= djk.pathTo(analyzer['search'],formatVertex(i))
                distance=djk.distTo(analyzer['search'],formatVertex(i))
                if distance<dist_menor_dest:
                    dist_menor_dest=distance
                    path=path_probable
    except:
        pass
    
    
    
    path_new=lt.newList('ARRAY_LIST')
    if lt.size(path)>0:
        
        for i in range(1,lt.size(path)+1):
            if not G.has_node(lt.getElement(path,i)['vertexA']):
                G.add_node(lt.getElement(path,i)['vertexA'])
                G.add_node(lt.getElement(path,i)['vertexB'])
            else:
                G.add_node(lt.getElement(path,i)['vertexB'])
            
            if 'T-' in lt.getElement(path,i)['vertexA']:
                cont_trans+=1

            dist=gr.getEdge(analyzer['grafo'],lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])['weight']
            dict_edges[(lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])]=round(dist,2)
            G.add_edge(lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])
            dist_total+=dist
            
            if mp.contains(analyzer['stops'],lt.getElement(path,i)['vertexA']):
                barrio_vertex=mp.get(analyzer['stops'],lt.getElement(path,i)['vertexA'])
                barrio_vertex=me.getValue(barrio_vertex)
                lt.addFirst(path_new,[lt.getElement(path,i)['vertexA'],dist,barrio_vertex['Neighborhood_Name']])
            else:
                lt.addFirst(path_new,[lt.getElement(path,i)['vertexA'],dist,'Transbordo'])

        if mp.contains(analyzer['stops'],lt.getElement(path,0)['vertexB']):
            barrio_vertex=mp.get(analyzer['stops'],lt.getElement(path,0)['vertexB'])
            barrio_vertex=me.getValue(barrio_vertex)
            lt.addLast(path_new,[lt.getElement(path,0)['vertexB'],0,barrio_vertex['Neighborhood_Name']])
        else:
            lt.addLast(path_new,[lt.getElement(path,0)['vertexB'],0,'Transbordo'])
        end_time=getTime()
        times=deltaTime(start_time,end_time)
        
        return True, dist_total, lt.size(path_new), cont_trans, path_new,G,dict_edges,round(times,3)
    else:
        end_time=getTime()
        times=deltaTime(start_time,end_time)
        return False,0, 0, 0, 0,0,0,0,0,round(times,3)

def getReq7(analyzer,ini):
    start_time=getTime()
    G=nx.Graph()
    G.add_node(ini)

    dict_edges={}
    existe_circulo=False
    dist_total=0
    path_new=None
    cont_trans=0
    cant_estaciones=0
    
    lst_adj=gr.adjacents(analyzer['grafo'],ini)

    dict_aux={}
    for i in lt.iterator(lst_adj):
        dict_aux[(ini,i)]=gr.getEdge(analyzer['grafo'],ini,i)['weight']
    
    gr.removeVertex(analyzer['grafo'],ini) #No sirve xd

    analyzer['search']=djk.Dijkstra(analyzer['grafo'],lt.getElement(lst_adj,1))
    

    for i in range(2,lt.size(lst_adj)+1):

        vertex_dest=lt.getElement(lst_adj,i)
        exist=djk.hasPathTo(analyzer['search'],vertex_dest)
        path_new=lt.newList('ARRAY_LIST')
        cont_trans=0
        dist_total=0
        
        if exist:
            existe_circulo=True
            path= djk.pathTo(analyzer['search'],vertex_dest)
            for i in range(1,lt.size(path)+1):
                if not G.has_node(lt.getElement(path,i)['vertexA']):
                    G.add_node(lt.getElement(path,i)['vertexA'])
                    G.add_node(lt.getElement(path,i)['vertexB'])
                else:
                    G.add_node(lt.getElement(path,i)['vertexB'])
                
                if 'T-' in lt.getElement(path,i)['vertexA']:
                    cont_trans+=1

                dist=gr.getEdge(analyzer['grafo'],lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])['weight']
                dict_edges[(lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])]=round(dist,2)
                G.add_edge(lt.getElement(path,i)['vertexA'],lt.getElement(path,i)['vertexB'])
                dist_total+=dist
                lt.addFirst(path_new,[lt.getElement(path,i)['vertexA'],dist])

            dist=dict_aux[(ini,vertex_dest)]
            dict_edges[(ini,vertex_dest)]=round(dist,2)
            G.add_edge(ini,vertex_dest)
            G.add_edge(ini,lt.getElement(lst_adj,1))
            dist_total+=dist
            lt.addLast(path_new,[lt.getElement(path,0)['vertexB'],0])
            cant_estaciones=lt.size(path_new)
            break
        else:
            analyzer['search']=djk.Dijkstra(analyzer['grafo'],vertex_dest)

    end_time=getTime()
    times=deltaTime(start_time,end_time)
    
    return existe_circulo,G, dist_total, path_new, cont_trans, dict_edges, cant_estaciones,round(times,3)

    

# Funciones de comparación

def compareStopIds(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1

def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1

def cmpByCode(movie1, movie2):

    if movie1>movie2:
        return 0
    else:
        return 1

#Funciones de Tiempo

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)

def deltaTime(start, end):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed

# Funciones de Ayuda

def formatVertex(service):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = service['Code'] + '-'
    name = name + service['Bus_Stop'][4:]
    return name

def formatArco(service):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = service['Code'] + '-'
    name = name + service['Bus_Stop'][4:]
    return name

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