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
import os
import config as cf
import sys
import threading
import controller
import networkx as nx
import matplotlib.pyplot as plt
from DISClib.ADT import list as lt
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

# Funciones de Print

def printMenu():
    print("Bienvenido")
    print("0- Cargar información de las rutas")
    print("1- Buscar camino posible entre dos estaciones")
    print("2- Buscar camino con menos paradas entre dos estaciones")
    print("3- Reconocer los componentes conectados")
    print("4- Planear el camino con distancia mínima entre dos puntos")
    print("5- Informar estaciones alcanzables desde un punto")
    print("6- Buscar el camino mínimo entreuna estacion y un vecindario")
    print("7- En contrar un camino circular dede un origen")

# Función crear controlador

def newController():
    control = controller.newController()
    return control

# Función Cargar Datos

def loadData(control,archiv,memory):
    movies= controller.loadData(control,archiv,memory)
    return movies


# Funciones para ejecutar el menú
def playLoadData():
    print('\nCuántos datos desea cargar?')
    print('1: 0.5% de los datos')
    print('2: 5% de los datos')
    print('3: 10% de los datos')
    print('4: 20% de los datos')
    print('5: 30% de los datos')
    print('6: 50% de los datos')
    print('7: 80% de los datos')
    print('8: 100% de los datos')
    resp=int(input())
    if resp==1:
        archiv='small.csv'
    elif resp==2:
        archiv='5pct.csv'
    elif resp==3:
        archiv='10pct.csv'
    elif resp==4:
        archiv='20pct.csv'
    elif resp==5:
        archiv='30pct.csv'
    elif resp==6:
        archiv='Ex.csv'
    elif resp==7:
        archiv='80pct.csv'
    elif resp==8:
        archiv='large.csv'
    
    resp=input(('\nDesea Conocer la memoria utilizada? '))
    resp=castBoolean(resp)
    vertices,arcos,cont_trans,time,memory= loadData(catalog,archiv,resp)
    
    os.system('cls')
    print('----------------------------------')
    print('Loaded Barcelona Transit data properties: ') 
    print('Total loaded Vertex: '+str(vertices))
    print('Total loaded Connection: '+str(arcos))
    print('----------------------------------')
    
    print(f'Tiempo de ejecución: {time:.3f}')
    print(f'Memoria Utilizada: {memory}\n')

def playReq1():
    os.system('cls')
    ini= input("Ingrese la estación de inicio: ")
    dest= input("Ingrese la estación de destino: ")
    resp,dist,cant_estaciones,cant_transbordo,path,G,dict_edges,times=controller.getReq1(catalog,ini,dest)
    if resp:
        print(f'\nLa distancia total del recorrido es {round(dist,2)}')
        print(f'El total de estaciones que contiene el camino es: {cant_estaciones}')
        print(f'El total de transbordos a realiazr es: {cant_transbordo}')
        print(f'\nLas estaciones a recorrer son:')
        if cant_estaciones<10:
            for i in lt.iterator(path): print(f'Estacion {i[0]}, distancia siguiente: {i[1]}')
            print('\n')
        else:
            for i in range(1,6): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('...')
            for i in range(cant_estaciones-5,cant_estaciones+1): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('\n')
        
        pos = nx.spring_layout(G)
        options = {
                    "font_size": 10,
                    "node_size": 600,
                    "node_color": "lightblue",
                    "edgecolors": "black",
                    "linewidths": 2,
                    "width": 2,
                    }
        print(f'Tiempo de ejecucíon: {times}')
        nx.draw_networkx(G,pos,**options)
        nx.draw_networkx_edge_labels(G,pos,edge_labels=dict_edges)
        plt.show()
    else:
        print(f'Tiempo de ejecucíon: {times}')
        print(f'\nNo existe un camino entre la estación: {ini} a la estación: {dest}')
  
def playReq2():
    os.system('cls')
    ini= input("Ingrese la estación de inicio: ")
    dest= input("Ingrese la estación de destino: ")
    resp,dist,cant_estaciones,cant_transbordo,path,G,dict_edges,times=controller.getReq2(catalog,ini,dest)
    if resp:
        print(f'\nLa distancia total del recorrido es {round(dist,2)}')
        print(f'El total de estaciones que contiene el camino es: {cant_estaciones}')
        print(f'El total de transbordos a realiazr es: {cant_transbordo}')
        print(f'\nLas estaciones a recorrer son:')
        if cant_estaciones<10:
            for i in lt.iterator(path): print(f'Estacion {i[0]}, distancia siguiente: {i[1]}')
            print('\n')
        else:
            for i in range(1,6): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('...')
            for i in range(cant_estaciones-5,cant_estaciones+1): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('\n')
        
        pos = nx.spring_layout(G)
        options = {
                    "font_size": 10,
                    "node_size": 600,
                    "node_color": "lightblue",
                    "edgecolors": "black",
                    "linewidths": 2,
                    "width": 2,
                    }
        print(f'Tiempo de ejecucíon: {times}')
        nx.draw_networkx(G,pos,**options)
        nx.draw_networkx_edge_labels(G,pos,edge_labels=dict_edges)
        plt.show()
    else:
        print(f'Tiempo de ejecucíon: {times}')
        print(f'\nNo existe un camino entre la estación: {ini} a la estación: {dest}')

def playReq3():
    os.system('cls')
    cant_conectados,mapa_componentes,times=controller.getReq3(catalog)
    print(f'El total de componentes conectados son: {cant_conectados}')
    if cant_conectados>5:
        contador=1
        for i in mapa_componentes:
            print(f'\nComponente conectado número: {i}')
            print('Cantidad de elementos conectados en este componente: '+str(mapa_componentes[i]['count']))
            if mapa_componentes[i]['count']>6:
                for j in range(1,4):
                    print('Estación: '+ lt.getElement(mapa_componentes[i]['lista_vertex'],j))
                print('...')
                for j in range(lt.size(mapa_componentes[i]['lista_vertex'])+1):
                    if lt.size(mapa_componentes[i]['lista_vertex'])-j<=3:
                        print('Estación: '+lt.getElement(mapa_componentes[i]['lista_vertex'],j))
            else:
                for j in range(1,4):
                    print('Estación: '+ lt.getElement(mapa_componentes[i]['lista_vertex'],j))
            if contador==5:
                break
            contador+=1
    print(f'Tiempo de ejecucíon: {times}')
    print('\n')

def playReq4():
    os.system('cls')
    lon_ini= float(input("Ingrese la Longitud geográfica inicial: "))
    lat_ini= float(input("Ingrese la Latitud geográfica inicial: "))
    lon_dest= float(input("Ingrese la Longitud geográfica final: "))
    lat_dest= float(input("Ingrese la Latitud geográfica final: "))
    resp,dist_ini,dist,dist_dest,cant_estaciones,cant_transbordo,path,G,dict_edges,times=controller.getReq4(catalog,lon_ini,lat_ini,lon_dest,lat_dest)
    
    if resp:
        print(f'\nLa distancia entre la ubicación inicial y la estación inicial es: {dist_ini}')
        print(f'La distancia total del recorrido es: {round(dist,2)}')
        print(f'La distancia entre la ubicación destino y la estación destino es: {dist_dest}')
        print(f'El total de estaciones que contiene el camino es: {cant_estaciones}')
        print(f'El total de transbordos a realiazr es: {cant_transbordo}')
        print(f'\nLas estaciones a recorrer son:')
        if cant_estaciones<10:
            for i in lt.iterator(path): print(f'Estacion {i[0]}, distancia siguiente: {i[1]}')
            print('\n')
        else:
            for i in range(1,6): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('...')
            for i in range(cant_estaciones-5,cant_estaciones+1): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('\n')
        
        pos = nx.spring_layout(G)
        options = {
                    "font_size": 10,
                    "node_size": 600,
                    "node_color": "lightblue",
                    "edgecolors": "black",
                    "linewidths": 2,
                    "width": 2,
                    }

        print(f'Tiempo de ejecucíon: {times}')
        nx.draw_networkx(G,pos,**options)
        nx.draw_networkx_edge_labels(G,pos,edge_labels=dict_edges)
        plt.show()
    else:
        print(f'Tiempo de ejecucíon: {times}')
        print(f'\nNo existe un camino entre la ubicación: [{lon_ini},{lat_ini}] a la ubicación: [{lon_dest},{lat_dest}]')

def playReq5():
    ini= input("Ingrese la estación de inicio: ")
    num= int(input("Ingrese el numero de conexiones máximas que desea: "))
    lst_adj,G,times=controller.getReq5(catalog,ini,num)
    
    print(f'Las estaciones alcanzables desde la estación: {ini} con un máximo de {num} conexiones son:\n\n')
    if lt.size(lst_adj)<10:
            for i in lt.iterator(lst_adj): print(f'Estacion: {i[0]}, Longitud: {i[1]}, Latitud: {i[2]}, Distancia: {i[3]}')
            print('\n')
    else:
        for i in range(1,6): print(f'Estacion: {lt.getElement(lst_adj,i)[0]}, Longitud: {lt.getElement(lst_adj,i)[1]}, Latitude: {lt.getElement(lst_adj,i)[2]}, Distancia: {lt.getElement(lst_adj,i)[3]}')
        print('...')
        for i in range(lt.size(lst_adj)-5,lt.size(lst_adj)+1): print(f'Estacion: {lt.getElement(lst_adj,i)[0]}, Longitud: {lt.getElement(lst_adj,i)[1]}, Latitude: {lt.getElement(lst_adj,i)[2]}, Distancia: {lt.getElement(lst_adj,i)[3]}')
        print('\n')
        
    pos = nx.spring_layout(G)
    options = {
                    "font_size": 10,
                    "node_size": 600,
                    "node_color": "lightblue",
                    "edgecolors": "black",
                    "linewidths": 2,
                    "width": 2,
                    }
    print(f'Tiempo de ejecucíon: {times}')
    nx.draw_networkx(G,pos,**options)
    plt.show()

def playReq6():
    os.system('cls')
    ini= input("Ingrese la estación de origen: ")
    barrio= input("Ingrese el bario de destino: ")
    resp,dist,cant_estaciones,cant_transbordo,path,G,dict_edges,times=controller.getReq6(catalog,ini,barrio)
    
    if resp:
        print(f'La distancia total del recorrido es: {round(dist,2)}')
        print(f'El total de estaciones que contiene el camino es: {cant_estaciones}')
        print(f'El total de transbordos a realizar es: {cant_transbordo}')
        print(f'\nLas estaciones a recorrer son:')
        if cant_estaciones<10:
            for i in lt.iterator(path): print(f'Estacion: {i[0]}, Barrio: {i[2]}, distancia siguiente: {i[1]}')
            print('\n')
        else:
            for i in range(1,6): print(f'Estacion: {lt.getElement(path,i)[0]}, Barrio: {lt.getElement(path,i)[2]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('...')
            for i in range(cant_estaciones-5,cant_estaciones+1): print(f'Estacion: {lt.getElement(path,i)[0]}, Barrio: {lt.getElement(path,i)[2]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('\n')
        
        pos = nx.spring_layout(G)
        options = {
                    "font_size": 10,
                    "node_size": 600,
                    "node_color": "lightblue",
                    "edgecolors": "black",
                    "linewidths": 2,
                    "width": 2,
                    }
        print(f'Tiempo de ejecucíon: {times}')
        nx.draw_networkx(G,pos,**options)
        nx.draw_networkx_edge_labels(G,pos,edge_labels=dict_edges)
        plt.show()
    else:
        print(f'Tiempo de ejecucíon: {times}')
        print(f'\nNo existe un camino entre la estacion: {ini} al barrio: {barrio}')

def playReq7():
    os.system('cls')
    ini= input("Ingrese la estación de inicio: ")
    existe,G,dist,path,cont_trans,dict_edges,cant_estaciones,times=controller.getReq7(catalog,ini)
    
    if existe:
        print(f'Si existe un camino circular desde la estación: {ini}')
        print(f'La distancia mínima del camino posible es: {dist}')
        print(f'Hay que realizar {cont_trans} transbordos')
        print(f'Las estaciones son:\n')
        if cant_estaciones>10:
            for i in range(1,6): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('...')
            for i in range(cant_estaciones-5,cant_estaciones+1): print(f'Estacion {lt.getElement(path,i)[0]}, distancia siguiente: {lt.getElement(path,i)[1]}')
            print('\n')
        else:
            for i in lt.iterator(path): print(f'Estacion {i[0]}, distancia siguiente: {i[1]}')
            print('\n')
        
        pos = nx.spring_layout(G)
        options = {
                    "font_size": 10,
                    "node_size": 600,
                    "node_color": "lightblue",
                    "edgecolors": "black",
                    "linewidths": 2,
                    "width": 2,
                    }

        print(f'Tiempo de ejecucíon: {times}')

        

        nx.draw_networkx(G,pos,**options)
        nx.draw_networkx_edge_labels(G,pos,edge_labels=dict_edges)
        plt.show()

    else:
        print(f'Tiempo de ejecucíon: {times}')
        print(f'No existe un  camino circular desde la estación: {ini}')


# Funciones Auxiliares

def castBoolean(value):
    """
    Convierte un valor a booleano
    """
    if value in ('True', 'true', 'TRUE', 'T', 't', '1', 1, True):
        return True
    else:
        return False

"""
Menu principal
"""

catalog = newController()

def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n')
        if int(inputs[0]) == 0:
            print("Cargando información de los archivos ....")
            
            playLoadData()
            
            
        elif int(inputs[0])==1:
            playReq1()
        elif int(inputs[0])==2:
            playReq2()
        elif int(inputs[0])==3:
            playReq3()
        elif int(inputs[0])==4:
            playReq4()
        elif int(inputs[0])==5:
            playReq5()
        elif int(inputs[0])==6:
            playReq6()
        elif int(inputs[0])==7:
            playReq7()
        else:
            sys.exit(0)

if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()