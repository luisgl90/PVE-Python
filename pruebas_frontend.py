from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic

class UI(QMainWindow):
	def __init__(self):
		super(UI,self).__init__()
		uic.loadUi("interfaz_app.ui",self)
		
		self.fase_frenado = 1
		self.fases_frenado = ['Eficiencia en frío','Calentamiento','Eficiencia en caliente',
			'Recuperación','Eficiencia de recuperación']

		#Fase de frenado - Labels de salida
		self.label_f_1 = self.findChild(QLabel,"label_fre_1")
		self.label_f_2 = self.findChild(QLabel,"label_fre_2")
		self.label_f_3 = self.findChild(QLabel,"label_fre_3")
		self.label_f_4 = self.findChild(QLabel,"label_fre_4")
		self.label_f_5 = self.findChild(QLabel,"label_fre_5")
		self.label_f_6 = self.findChild(QLabel,"label_fre_6")
		#Fase de frenado - Labels de título
		self.label_f_fase = self.findChild(QLabel,"label_fre_fase")
		self.label_f_vx = self.findChild(QLabel,"label_fre_vx")
		self.label_f_ax = self.findChild(QLabel,"label_fre_ax")
		self.label_f_fp = self.findChild(QLabel,"label_fre_fp")
		self.label_f_df_Td = self.findChild(QLabel,"label_fre_df_Td")
		self.label_f_Ti = self.findChild(QLabel,"label_fre_Ti")
		self.label_f_t_dr = self.findChild(QLabel,"label_fre_t_dr")

		self.button_f_fase = self.findChild(QPushButton,"button_fre_fase")
		self.button_f_fase.clicked.connect(self.cambiar_fase)

		#Ocultar labels iniciales
		self.label_f_5.hide()
		self.label_f_6.hide()
		self.label_f_Ti.hide()
		self.label_f_t_dr.hide()

		self.show()

	@pyqtSlot()
	def cambiar_fase(self):
		self.fase_frenado = self.fase_frenado + 1
		if self.fase_frenado>5:
			self.fase_frenado=1
		print(f'Siguiente fase -> Fase {self.fase_frenado}')
		self.label_f_fase.setText(self.fases_frenado[self.fase_frenado-1])
		if self.fase_frenado in (2,4):
			self.label_f_5.show()
			self.label_f_6.show()
			self.label_f_Ti.show()
			self.label_f_t_dr.show()
			
			if self.fase_frenado==2:
				self.label_f_4.setText('Td (°C)')
				self.label_f_6.setText('t (s)')

			if self.fase_frenado==4:
				self.label_f_4.setText('Td (°C)')
				self.label_f_6.setText('dr (m)')
		else:
			self.label_f_5.hide()
			self.label_f_6.hide()
			self.label_f_Ti.hide()
			self.label_f_t_dr.hide()
			self.label_f_4.setText('df (m)')
		
		if self.fase_frenado>=5:
			self.button_f_fase.setText('Finalizar')
		else:
			self.button_f_fase.setText('Siguiente fase')

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	UIWindow = UI()
	app.exec_()