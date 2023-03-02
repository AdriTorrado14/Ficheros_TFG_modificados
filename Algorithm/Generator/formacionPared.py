import math
import numpy as np

from PySide2 import QtCore, QtGui, QtWidgets

from room import Room
from human import Human
from linea import Linea

from collections import defaultdict
from scipy.spatial import distance

class FormacionPared (QtWidgets.QGraphicsItem):
    def __init__(self, puntos, a, b, h):
        super(FormacionPared, self).__init__()

        regenerateScene = True
        while regenerateScene:

            regenerateScene = False

            # Inicialización de los elementos que aparecen en la clase.
            self.puntos = puntos
            self.a = a
            self.b = b
            self.h = h
            habitacion_Modificada = self.h

            co1x = self.a.xPos # Coordenada 'x' del humano 1.
            co1y = self.a.yPos # Coordenada 'y' del humano 1.
            co1_2x = self.b.xPos # Coordenada 'x' del humano 2.
            co1_2y = self.b.yPos # Coordenada 'y' del humano 2.

            x_pm = (co1x + co1_2x) / 2 
            y_pm = (co1y + co1_2y) / 2

            hum = (x_pm, y_pm) # Punto medio de los humanos.

            self.puntoMedio = QtCore.QPointF(x_pm, y_pm) # Asignación punto medio.

            punto1 = QtCore.QPointF(co1x, co1y) # Asignación punto1.
            punto2 = QtCore.QPointF(co1_2x, co1_2y) # Asignacion punto2.
            self.lineaNueva = QtCore.QLineF(punto1, punto2) # Asignacion nueva linea.

            # Creación de puntos involucrados.
            PuntoMedio = QtCore.QPointF(x_pm, y_pm) # Punto medio de los humanos.
            punto_human = QtCore.QPointF(co1x, co1y) # Punto humano 1.
            punto_human2 = QtCore.QPointF(co1_2x, co1_2y) # Punto humano 2.


            # Asignación de los humanos como poligonos.
            RectanguloHumano = a.polygon() # Humano 1.
            RectanguloHumano2 = b.polygon() # Humano 2.
            ListaPoligonosHumanos = [] # Lista que guarda los objetos que aparecen en el escenario.
            ListaPoligonosHumanos.append(RectanguloHumano)
            ListaPoligonosHumanos.append(RectanguloHumano2)

            ############################################################################################
            # Inicio del metodo que presenta la nueva pared del escenario.

            # Transformación de la lista anidadas "puntos" en una lista sin anidar.
            puntos_lista = []
            for p in range(len(puntos)):
                for j in range(len(puntos[p])):
                    puntos_lista.append(puntos[p][j])

            lista_x = puntos_lista[::2] # Divide "puntos_lista" y solo aparece las posiciones correspondientes a 'x'.
            lista_y = puntos_lista[1::2] # Divide "puntos_lista" y solo aparece las posiciones correspondientes a 'y'.

            resta_x = []
            resta_y = []
            for k in range(len(lista_x)-1):
                resta_x.append(lista_x[k+1]-lista_x[k]) # Contiene el resultado de restar el posterior al anterior (posiciones del eje x). Lo guarda en una lista.
            for l in range(len(lista_y)-1):
                resta_y.append(lista_y[l+1]-lista_y[l]) # Contiene el resultado de restar el posterior al anterior (posiciones del eje y). Lo guarda en una lista. 

            try:
                valor_pendiente = [int(punto_y)/int(punto_x) for punto_y, punto_x in zip(resta_y,resta_x)] # Calculo de las distintas pendientes.
            except ZeroDivisionError:
                break

            # Diccionario en el que se guarda el segmento y el valor de su pendiente.
            aux = defaultdict(list)
            for index, item in enumerate(valor_pendiente):
                aux[item].append(index)
            result = {item: indexs for item, indexs in aux.items() if len(indexs) > 1}

            # Convierte el diccionario en una lista.
            indices = list(result.keys()) # Guarda el valor de la pendiente si hay dos o más iguales.
            # Guarda las posiciones en la que las pendientes son iguales. Si pusiera un [0,4] esto indica que las pendientes son iguales.
            # en los segmentos formados por los puntos 0 - 1 y por los puntos 4 - 5.
            posiciones = list(result.values())

            ############################################################################################
            # Procedimiento para ver si el punto medio esta situado entre los dos puntos que forman el segmento.
            # Tenemos una lista que nos dice el valor de las pendientes, y otra lista que nos muestra los segmentos.
            # con pendientes iguales. Si la pendiente es igual, esto nos indica que los segmentos son paralelos. 

            # Variables auxiliares.
            listas = []
            distPuntos = [] # Distancia entre punto inicial y punto final de un segmento.
            distPM_P1 = [] # Distancia entre el punto inicial de un segmento y el punto medio de las dos personas.
            distPM_P2 = [] # Distancia entre el punto final de un segmento y el punto medio de las dos personas.
            longitud_lista = []
            lmod = [] # Guarda los puntos cuyos segmentos formantes son paralelos.

            aux = []    
            listaComp = [] # Lista que recoge los resultados de la comparación. "1" indica que el punto medio esta entre los puntos inicio y final, "0" lo contrario.
            laux = []

            contador = 0
            cont = 0

            listaTemporal = []  
            listaIndices = []
            ListaParedN = []
            ListaUnionHumanos = []

            for m in range(len(posiciones)):
                for h in range(len(posiciones[m])):
                    contador = contador +1

            # Para poder calcular los puntos de la nueva pared que pasan por el punto medio se necesitan que dos o mas segmentos.
            # sean paralelos. Funciona para 6 o menos segmentos.
            
            if ((len(posiciones) <= 3 and len(posiciones) != 0) and (contador == 2 or contador == 4 or contador == 6) and not(len(posiciones) == 2 and contador == 6)): 
                for m in range(len(posiciones)):
                    for h in range(len(posiciones[m])):
                        auxiliar = posiciones[m][h]
                        listas = [puntos[auxiliar], puntos[auxiliar+1]]
                        lmod.append(listas)

                        distancia_entreVertice = distance.euclidean(puntos[auxiliar], puntos[auxiliar+1]) # Calcula la distancia existente entre el punto inicial y punto final del segmento.
                        distPuntos.append(distancia_entreVertice)

                        distanciaPM_P1 = distance.euclidean(hum, puntos[auxiliar]) # Calcula la distancia entre el punto medio de las personas y el punto inicial del segmento.
                        distPM_P1.append(distanciaPM_P1)
                    
                        distanciaPM_P2 = distance.euclidean(hum, puntos[auxiliar+1]) # Calcula la distancia entre el punto medio de las personas y el punto final del segmento.
                        distPM_P2.append(distanciaPM_P2)

                        x = len(distPM_P2) # Para saber la longitud de las listas anteriores. Tienen que tener el mismo tamaño. 
                        if x > 0:
                            longitud_lista = np.arange(x)
                
                for v in range(len(longitud_lista)):
                    aux.append(longitud_lista[v])

                # Comparación para ver si el punto medio esta entre punto inicial y el punto final del segmento.
                # Si esta, introduce un 1 en la lista. Si no esta, introduce un 0. 
                for c in range(len(aux)):
                    if ((distPuntos[c]**2 + distPM_P1[c]**2 >= distPM_P2[c]**2 and distPuntos[c]**2 + distPM_P2[c]**2 >= distPM_P1[c]**2)):
                        listaComp.append(1)
                    else:
                        listaComp.append(0)

                ########################################################################################
                # Sabemos que el punto medio tiene que estar entre dos segmentos que sean paralelos y que la nueva
                # pared tiene que pasar por ese punto y que sea perpendicular respecto a los dos segmentos. Esto nos lleva
                # a utilizar el teorema del coseno para averiguar los distintos ángulos que se forman en el
                # escenario. Una vez tengamos los ángulos, utilizamos las razones trigonómetricas para calcular las
                # distintas proyecciones y poder calcular los dos puntos nuevos. Estos dos puntos crearan un segmento que
                # pasa por el punto medio de las personas y que divide el espacio de la habitación.
                
                # Transformación. Transformamos la lista anidada "lmod" que contiene los puntos formados por los segmentos que son
                # paralelos en una lista sin anidar.
                for mi in range(len(lmod)):
                    for hi in range(len(lmod[mi])):
                        auxi = lmod[mi][hi]
                        laux.append(auxi)
                        
                # Calculo de los puntos.
                for ti in range(len(listaComp)):
                    cont = cont +1
                    if cont == 0:
                        break
                    elif (cont == 2):
                        if (listaComp[0] == 1 and listaComp[1] == 1):

                            listaTemporal.append(posiciones[0])

                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A = (distPM_P2[0]**2 - distPM_P1[0]**2 - distPuntos[0]**2) / (-2 * distPM_P1[0] * distPuntos[0]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA =math.acos(A); anguloA = cosA * (180 / math.pi)

                            B = (distPM_P1[0]**2 - distPM_P2[0]**2 - distPuntos[0]**2) / (-2 * distPM_P2[0] * distPuntos[0]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB = math.acos(B); anguloB = cosB * (180 / math.pi)
                
                            C = (distPuntos[0]**2 - distPM_P2[0]**2 - distPM_P1[0]**2) / (-2 * distPM_P2[0] * distPM_P1[0]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC = math.acos(C); anguloC = cosC * (180 / math.pi)
                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA = math.radians(anguloA); m = distPM_P1[0] * math.cos(angA)                            
                            angB = math.radians(anguloB); n = distPM_P2[0] * math.cos(angB)
                            
                            # Para averiguar el punto que divide a ese segmento.
                            razon = m / n # Razon entre segmentos
                            X = ((laux[0][0] + (razon * laux[1][0])) / (1 + razon)) # Punto X de la intersección.
                            Y = ((laux[0][1] + (razon * laux[1][1])) / (1 + razon)) # Punto Y de la intersección.

                            """##### Segundo Segmento #####
                            ############################"""
                
                            A_2 = (distPM_P2[1]**2 - distPM_P1[1]**2 - distPuntos[1]**2) / (-2 * distPM_P1[1] * distPuntos[1]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA_2 =math.acos(A_2); anguloA_2 = cosA_2 * (180 / math.pi)

                            B_2 = (distPM_P1[1]**2 - distPM_P2[1]**2 - distPuntos[1]**2) / (-2 * distPM_P2[1] * distPuntos[1]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB_2 = math.acos(B_2); anguloB_2 = cosB_2 * (180 / math.pi)
                
                            C_2 = (distPuntos[1]**2 - distPM_P2[1]**2 - distPM_P1[1]**2) / (-2 * distPM_P2[1] * distPM_P1[1]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC_2 = math.acos(C_2); anguloC_2 = cosC_2 * (180 / math.pi)

                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA_2 = math.radians(anguloA_2); m_2 = distPM_P1[1] * math.cos(angA_2)
                            angB_2 = math.radians(anguloB_2); n_2 = distPM_P2[1] * math.cos(angB_2)

                            # Para averiguar el punto que divide a ese segmento.
                            razon_2 = m_2 / n_2 # Razon entre segmentos
                            X_2 = ((laux[2][0] + (razon_2 * laux[3][0])) / (1 + razon_2)) # Punto X de la segunda intersección.
                            Y_2 = ((laux[2][1] + (razon_2 * laux[3][1])) / (1 + razon_2)) # Punto Y de la segunda intersección.
                            
                            break
                        
                    elif (cont == 4):
                        if (listaComp[0] == 1 and listaComp[1] == 1):
                            listaTemporal.append(posiciones[0])
                            A = (distPM_P2[0]**2 - distPM_P1[0]**2 - distPuntos[0]**2) / (-2 * distPM_P1[0] * distPuntos[0]); cosA =math.acos(A); cosA =math.acos(A); anguloA = cosA * (180 / math.pi)
                            B = (distPM_P1[0]**2 - distPM_P2[0]**2 - distPuntos[0]**2) / (-2 * distPM_P2[0] * distPuntos[0]); cosB = math.acos(B); anguloB = cosB * (180 / math.pi)
                            C = (distPuntos[0]**2 - distPM_P2[0]**2 - distPM_P1[0]**2) / (-2 * distPM_P2[0] * distPM_P1[0]); cosC = math.acos(C); anguloC = cosC * (180 / math.pi)
                            angA = math.radians(anguloA); m = distPM_P1[0] * math.cos(angA)
                            angB = math.radians(anguloB); n = distPM_P2[0] * math.cos(angB)
                            razon = m / n 
                            X = ((laux[0][0] + (razon * laux[1][0])) / (1 + razon)); Y = ((laux[0][1] + (razon * laux[1][1])) / (1 + razon)) 

                            """##### Segundo Segmento #####
                            ############################"""
                            A_2 = (distPM_P2[1]**2 - distPM_P1[1]**2 - distPuntos[1]**2) / (-2 * distPM_P1[1] * distPuntos[1]); cosA_2 =math.acos(A_2); anguloA_2 = cosA_2 * (180 / math.pi)
                            B_2 = (distPM_P1[1]**2 - distPM_P2[1]**2 - distPuntos[1]**2) / (-2 * distPM_P2[1] * distPuntos[1]); cosB_2 = math.acos(B_2); anguloB_2 = cosB_2 * (180 / math.pi)
                            C_2 = (distPuntos[1]**2 - distPM_P2[1]**2 - distPM_P1[1]**2) / (-2 * distPM_P2[1] * distPM_P1[1]); cosC_2 = math.acos(C_2); anguloC_2 = cosC_2 * (180 / math.pi)
                            angA_2 = math.radians(anguloA_2); m_2 = distPM_P1[1] * math.cos(angA_2)
                            angB_2 = math.radians(anguloB_2); n_2 = distPM_P2[1] * math.cos(angB_2)
                            razon_2 = m_2 / n_2 
                            X_2 = ((laux[2][0] + (razon_2 * laux[3][0])) / (1 + razon_2)); Y_2 = ((laux[2][1] + (razon_2 * laux[3][1])) / (1 + razon_2)) 
                            
                            break
                                                        
                        elif (listaComp[2] == 1 and listaComp[3] == 1):
                            listaTemporal.append(posiciones[1])
                            A = (distPM_P2[2]**2 - distPM_P1[2]**2 - distPuntos[2]**2) / (-2 * distPM_P1[2] * distPuntos[2]); cosA =math.acos(A); anguloA = cosA * (180 / math.pi)
                            B = (distPM_P1[2]**2 - distPM_P2[2]**2 - distPuntos[2]**2) / (-2 * distPM_P2[2] * distPuntos[2]); cosB = math.acos(B); anguloB = cosB * (180 / math.pi)
                            C = (distPuntos[2]**2 - distPM_P2[2]**2 - distPM_P1[2]**2) / (-2 * distPM_P2[2] * distPM_P1[2]); cosC = math.acos(C); anguloC = cosC * (180 / math.pi)
                            angA = math.radians(anguloA); m = distPM_P1[2] * math.cos(angA)
                            angB = math.radians(anguloB); n = distPM_P2[2] * math.cos(angB)
                            razon = m / n 
                            X = ((laux[4][0] + (razon * laux[5][0])) / (1 + razon)); Y = ((laux[4][1] + (razon * laux[5][1])) / (1 + razon))
                        
                            """##### Segundo Segmento #####
                            ############################"""
                            A_2 = (distPM_P2[3]**2 - distPM_P1[3]**2 - distPuntos[3]**2) / (-2 * distPM_P1[3] * distPuntos[3]); cosA_2 =math.acos(A_2); anguloA_2 = cosA_2 * (180 / math.pi)
                            B_2 = (distPM_P1[3]**2 - distPM_P2[3]**2 - distPuntos[3]**2) / (-2 * distPM_P2[3] * distPuntos[3]); cosB_2 = math.acos(B_2); anguloB_2 = cosB_2 * (180 / math.pi)
                            C_2 = (distPuntos[3]**2 - distPM_P2[3]**2 - distPM_P1[3]**2) / (-2 * distPM_P2[3] * distPM_P1[3]); cosC_2 = math.acos(C_2); anguloC_2 = cosC_2 * (180 / math.pi)
                            angA_2 = math.radians(anguloA_2); m_2 = distPM_P1[3] * math.cos(angA_2)
                            angB_2 = math.radians(anguloB_2); n_2 = distPM_P2[3] * math.cos(angB_2)
                            razon_2 = m_2 / n_2 
                            X_2 = ((laux[6][0] + (razon_2 * laux[7][0])) / (1 + razon_2)); Y_2 = ((laux[6][1] + (razon_2 * laux[7][1])) / (1 + razon_2))

                            break

                    elif (cont == 6):
                        if (listaComp[0] == 1 and listaComp[1] == 1):
                            listaTemporal.append(posiciones[0])
                            A = (distPM_P2[0]**2 - distPM_P1[0]**2 - distPuntos[0]**2) / (-2 * distPM_P1[0] * distPuntos[0]); cosA =math.acos(A); anguloA = cosA * (180 / math.pi)
                            B = (distPM_P1[0]**2 - distPM_P2[0]**2 - distPuntos[0]**2) / (-2 * distPM_P2[0] * distPuntos[0]); cosB = math.acos(B); anguloB = cosB * (180 / math.pi)
                            C = (distPuntos[0]**2 - distPM_P2[0]**2 - distPM_P1[0]**2) / (-2 * distPM_P2[0] * distPM_P1[0]); cosC = math.acos(C); anguloC = cosC * (180 / math.pi)
                            angA = math.radians(anguloA); m = distPM_P1[0] * math.cos(angA)
                            angB = math.radians(anguloB); n = distPM_P2[0] * math.cos(angB)
                            razon = m / n 
                            X = ((laux[0][0] + (razon * laux[1][0])) / (1 + razon)); Y = ((laux[0][1] + (razon * laux[1][1])) / (1 + razon))

                            """##### Segundo Segmento #####
                            ############################"""
                            A_2 = (distPM_P2[1]**2 - distPM_P1[1]**2 - distPuntos[1]**2) / (-2 * distPM_P1[1] * distPuntos[1]); cosA_2 =math.acos(A_2); anguloA_2 = cosA_2 * (180 / math.pi)
                            B_2 = (distPM_P1[1]**2 - distPM_P2[1]**2 - distPuntos[1]**2) / (-2 * distPM_P2[1] * distPuntos[1]); cosB_2 = math.acos(B_2); anguloB_2 = cosB_2 * (180 / math.pi)
                            C_2 = (distPuntos[1]**2 - distPM_P2[1]**2 - distPM_P1[1]**2) / (-2 * distPM_P2[1] * distPM_P1[1]); cosC_2 = math.acos(C_2); anguloC_2 = cosC_2 * (180 / math.pi)
                            angA_2 = math.radians(anguloA_2); m_2 = distPM_P1[1] * math.cos(angA_2)
                            angB_2 = math.radians(anguloB_2); n_2 = distPM_P2[1] * math.cos(angB_2)
                            razon_2 = m_2 / n_2 
                            X_2 = ((laux[2][0] + (razon_2 * laux[3][0])) / (1 + razon_2)); Y_2 = ((laux[2][1] + (razon_2 * laux[3][1])) / (1 + razon_2))

                            break

                        elif (listaComp[2] == 1 and listaComp[3] == 1):
                            listaTemporal.append(posiciones[1])
                            A = (distPM_P2[2]**2 - distPM_P1[2]**2 - distPuntos[2]**2) / (-2 * distPM_P1[2] * distPuntos[2]); cosA =math.acos(A); anguloA = cosA * (180 / math.pi)
                            B = (distPM_P1[2]**2 - distPM_P2[2]**2 - distPuntos[2]**2) / (-2 * distPM_P2[2] * distPuntos[2]); cosB = math.acos(B); anguloB = cosB * (180 / math.pi)
                            C = (distPuntos[2]**2 - distPM_P2[2]**2 - distPM_P1[2]**2) / (-2 * distPM_P2[2] * distPM_P1[2]); cosC = math.acos(C); anguloC = cosC * (180 / math.pi)
                            angA = math.radians(anguloA); m = distPM_P1[2] * math.cos(angA)
                            angB = math.radians(anguloB); n = distPM_P2[2] * math.cos(angB)
                            razon = m / n
                            X = ((laux[4][0] + (razon * laux[5][0])) / (1 + razon)); Y = ((laux[4][1] + (razon * laux[5][1])) / (1 + razon))

                            """##### Segundo Segmento #####
                            ############################"""
                            A_2 = (distPM_P2[3]**2 - distPM_P1[3]**2 - distPuntos[3]**2) / (-2 * distPM_P1[3] * distPuntos[3]); cosA_2 =math.acos(A_2); anguloA_2 = cosA_2 * (180 / math.pi)
                            B_2 = (distPM_P1[3]**2 - distPM_P2[3]**2 - distPuntos[3]**2) / (-2 * distPM_P2[3] * distPuntos[3]); cosB_2 = math.acos(B_2); anguloB_2 = cosB_2 * (180 / math.pi)
                            C_2 = (distPuntos[3]**2 - distPM_P2[3]**2 - distPM_P1[3]**2) / (-2 * distPM_P2[3] * distPM_P1[3]); cosC_2 = math.acos(C_2); anguloC_2 = cosC_2 * (180 / math.pi)
                            angA_2 = math.radians(anguloA_2); m_2 = distPM_P1[3] * math.cos(angA_2)
                            angB_2 = math.radians(anguloB_2); n_2 = distPM_P2[3] * math.cos(angB_2)
                            razon_2 = m_2 / n_2 
                            X_2 = ((laux[6][0] + (razon_2 * laux[7][0])) / (1 + razon_2)); Y_2 = ((laux[6][1] + (razon_2 * laux[7][1])) / (1 + razon_2))

                            break

                        elif (listaComp[4] == 1 and listaComp[5] == 1):
                            listaTemporal.append(posiciones[2])
                            A = (distPM_P2[4]**2 - distPM_P1[4]**2 - distPuntos[4]**2) / (-2 * distPM_P1[4] * distPuntos[4]); cosA =math.acos(A); anguloA = cosA * (180 / math.pi)
                            B = (distPM_P1[4]**2 - distPM_P2[4]**2 - distPuntos[4]**2) / (-2 * distPM_P2[4] * distPuntos[4]); cosB = math.acos(B); anguloB = cosB * (180 / math.pi)
                            C = (distPuntos[4]**2 - distPM_P2[4]**2 - distPM_P1[4]**2) / (-2 * distPM_P2[4] * distPM_P1[4]); cosC = math.acos(C); anguloC = cosC * (180 / math.pi)
                            angA = math.radians(anguloA); m = distPM_P1[4] * math.cos(angA)
                            angB = math.radians(anguloB); n = distPM_P2[4] * math.cos(angB)
                            razon = m / n 
                            X = ((laux[8][0] + (razon * laux[9][0])) / (1 + razon)); Y = ((laux[8][1] + (razon * laux[9][1])) / (1 + razon))

                            """##### Segundo Segmento #####
                            ############################"""
                            A_2 = (distPM_P2[5]**2 - distPM_P1[5]**2 - distPuntos[5]**2) / (-2 * distPM_P1[5] * distPuntos[5]); cosA_2 =math.acos(A_2); anguloA_2 = cosA_2 * (180 / math.pi)
                            B_2 = (distPM_P1[5]**2 - distPM_P2[5]**2 - distPuntos[5]**2) / (-2 * distPM_P2[5] * distPuntos[5]); cosB_2 = math.acos(B_2); anguloB_2 = cosB_2 * (180 / math.pi)
                            C_2 = (distPuntos[5]**2 - distPM_P2[5]**2 - distPM_P1[5]**2) / (-2 * distPM_P2[5] * distPM_P1[5]); cosC_2 = math.acos(C_2); anguloC_2 = cosC_2 * (180 / math.pi)
                            angA_2 = math.radians(anguloA_2); m_2 = distPM_P1[5] * math.cos(angA_2)
                            angB_2 = math.radians(anguloB_2); n_2 = distPM_P2[5] * math.cos(angB_2)
                            razon_2 = m_2 / n_2 
                            X_2 = ((laux[10][0] + (razon_2 * laux[11][0])) / (1 + razon_2)); Y_2 = ((laux[10][1] + (razon_2 * laux[11][1])) / (1 + razon_2))

                            break

                try:
                    punto_Segmento1 = QtCore.QPointF(X,Y) # Coordenada punto 1 de la nueva pared.

                    punto_Segmento2 = QtCore.QPointF(X_2,Y_2) #Coordenada punto 2 de la nueva pared.
                    
                    lineaNuevaPared = QtCore.QLineF(punto_Segmento1, punto_Segmento2) # Linea de la nueva pared.

                    lineaHumano = QtCore.QLineF(punto_human, punto_human2) # Linea de union de los humanos.

                    # Asignación de la línea nueva como poligono y linea correspondiente a la union de los humanos como poligono.
                    ListaUnionHumanos.append(punto_human)
                    ListaUnionHumanos.append(punto_human2)

                    PoligonoUnion = QtGui.QPolygonF()
                    PoligonoUnion.append(ListaUnionHumanos)

                    ListaParedN.append(punto_Segmento1)
                    ListaParedN.append(punto_Segmento2)

                    PoligonoLinea = QtGui.QPolygonF()
                    PoligonoLinea.append(ListaParedN)

                    ####################################################################################
                    # Condiciones para que la que la nueva pared formada en el escenario no intersecte con ningun humano.
                    
                    if ((PoligonoLinea.intersects(RectanguloHumano) == False) and (PoligonoLinea.intersects(RectanguloHumano2) == False) and (PoligonoUnion.intersects(PoligonoLinea) == True)):

                        # Introducción de los nuevos puntos a la polilinea.
                        for yip in puntos:
                            indices_Puntos = len(puntos)
                            listaIndices = np.arange(indices_Puntos)

                        for tip in range(len(listaIndices)):
                            if listaTemporal[0][0] == listaIndices[tip]:
                                habitacion_Modificada.insert(tip+1, punto_Segmento1) 
                                habitacion_Modificada.insert(tip+2, punto_Segmento2)
                                habitacion_Modificada.insert(tip+3, punto_Segmento1)                    

                except UnboundLocalError:
                    break
