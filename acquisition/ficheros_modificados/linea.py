import math

from PySide2 import QtCore, QtGui, QtWidgets

class Linea (QtWidgets.QGraphicsItem):
    def __init__(self, a, b):
        super(Linea, self).__init__()

        # Inicializacion de los elementos que aparecen en la clase 
        self.a = a
        self.b = b

        XPuntoMedio = (self.a.xPos + self.b.xPos) / 2
        YPuntoMedio = (self.a.yPos + self.b.yPos) / 2

        co1x = self.a.xPos # Coordenada 'x' del humano 1.
        co1y = self.a.yPos # Coordenada 'y' del humano 1.
        co1_2x = self.b.xPos # Coordenada 'x' del humano 2.
        co1_2y = self.b.yPos # Coordenada 'y' del humano 2.

        s1 = co1x - co1_2x
        s2 = co1y - co1_2y
        d = math.sqrt(s1*s1 + s2*s2) # Distancia existente entre las dos coordenadas

        self.length = d # Asignacion de la distantcia.

        self.text = QtGui.QStaticText(f"{self.length/100:.2f}" + ' m') # Texto

        self.puntoMedio = QtCore.QPointF(XPuntoMedio, YPuntoMedio) # Asignación punto medio.
        self.BoundingRect = QtCore.QRectF(-10, -10, 20, 20) 

        punto1 = QtCore.QPointF(co1x, co1y) # Asignación punto1.
        punto2 = QtCore.QPointF(co1_2x, co1_2y) # Asignacion punto2
        self.lineaNueva = QtCore.QLineF(punto1, punto2) # Asignacion linea de union de los humanos 
        
    def boundingRect(self):
        return self.BoundingRect

    def paint(self, painter, option, widget):
        if (self.length > 65):
            painter.drawLine(self.lineaNueva) # Linea que une la posicion de los dos humanos.
            painter.drawStaticText(self.puntoMedio, self.text) # Distancia en metros que presentan los dos humanos.
