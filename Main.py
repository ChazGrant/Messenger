from PyQt5 import QtWidgets
from Auth import Auth

QT = QtWidgets.QApplication([])
window = Auth()
window.show()
QT.exec_()