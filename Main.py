from PyQt5 import QtWidgets
from Auth import Auth

app = QtWidgets.QApplication([])
window = Auth()
window.show()
app.exec_()
