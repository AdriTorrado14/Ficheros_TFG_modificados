import math

from PySide2 import QtCore, QtGui, QtWidgets


class Line(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(Line, self).__init__()
        self.colour = QtCore.Qt.black

    def paint(self, painter, option, widget):
        linea = QtCore.QLineF()
        painter.setBrush(self.colour)
        painter.drawLine(linea)

