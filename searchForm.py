import searchFormUI
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QPoint


class searchForm(searchFormUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.oldPos = self.pos()

        self.text = ""

        self.searchButton.pressed.connect(self.setText)
        self.cancelButton.pressed.connect(self.close)
        self.exitButton.pressed.connect(self.close)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def setText(self):
        self.text = self.textEdit.toPlainText()
        print(self.text)
        print(self.checkBox.isChecked())
        print(self.checkBox_2.isChecked())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = searchForm()
    window.setFixedSize(465, 260)
    window.show()
    app.exec_()
