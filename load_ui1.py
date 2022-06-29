from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QPushButton, QLabel
from PyQt5 import uic
import sys

class UI(QDialog):
	def __init__(self):
		super(UI,self).__init__()
		uic.loadUi("interfaz_estabilidad1.ui",self)
		self.show()


app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()