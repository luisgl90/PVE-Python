# Prueba multithreading usando Arduino UNO y Arduino Mega conectados por USB
# Se tiene un objeto que hereda de QThread para cada conexión y un objeto 
#  para la adquisición con un tiempo de muestreo determinado

from ast import Continue
import nidaqmx as daq
import math
import time
#import numpy 
#import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3
import threading
import serial
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
from bitstring import BitArray
from pyqtgraph import PlotWidget, plot, mkPen
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel,QComboBox,QTabWidget
from PyQt5.QtCore import pyqtSlot,QTimer,Qt,QObject, QThread, pyqtSignal
from PyQt5 import uic


class UI(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.tab_index = 0
		self.fase_frenado = 1
		self.fases_frenado = ['Eficiencia en frío','Calentamiento','Eficiencia en caliente',
			'Recuperación','Eficiencia de recuperación']
		self.setupUi()
		#icon = QtGui.QIcon()
		#icon.addPixmap(QtGui.QPixmap("PyShine.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		#self.setWindowIcon(icon)
		self.thread={}
		self.pause = False
		self.val1 = 0.0
		self.val2 = 0.0

		self.xdata = []
		self.ydata = []
		self.line1 = None
		self.t = -0.1

		self.start_workers()

		self.timer = QTimer()

	def setupUi(self):
		uic.loadUi("interfaz_app.ui",self)
				
		self.tabs_pruebas = self.findChild(QTabWidget,"tabs_pruebas")
		self.tabs_pruebas.currentChanged.connect(self.tab_change)
		self.tab_index = self.tabs_pruebas.currentIndex()
		print(f'Current tab: {self.tab_index}')

		self.button_start = self.findChild(QPushButton,"button_start")
		self.button_start.clicked.connect(self.start_acquisition)
		self.button_stop = self.findChild(QPushButton,"button_stop")
		self.button_stop.clicked.connect(self.stop_acquisition)
		self.button_stop.setEnabled(False)

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
		#Fase de frenado - Ocultar labels iniciales
		self.label_f_5.hide()
		self.label_f_6.hide()
		self.label_f_Ti.hide()
		self.label_f_t_dr.hide()
		self.button_f_fase = self.findChild(QPushButton,"button_fre_fase")
		self.button_f_fase.clicked.connect(self.cambiar_fase)
		self.button_f_rst = self.findChild(QPushButton,"button_fre_rst")
		self.button_f_rst.clicked.connect(self.reiniciar_fase)

		#Fase de frenado - Labels de salida
		self.label_e_vx = self.findChild(QLabel,"label_est_vx")
		self.label_e_ay = self.findChild(QLabel,"label_est_ay")
		self.label_e_delta = self.findChild(QLabel,"label_est_delta")
		self.label_e_beta = self.findChild(QLabel,"label_est_beta")
		self.label_e_phi = self.findChild(QLabel,"label_est_phi")

		#Fase de frenado - Labels de salida
		self.label_v_ax = self.findChild(QLabel,"label_vib_ax")
		self.label_v_ay = self.findChild(QLabel,"label_vib_ay")
		self.label_v_az = self.findChild(QLabel,"label_vib_az")


		##----------INSERTAR OTRAS PRUEBAS----------##

		#Modo de prueba - ComboBox
		self.combo_prueba = self.findChild(QComboBox,"comboPrueba")
		#Modo de prueba - Labels de título
		self.label_p_1 = self.findChild(QLabel,"label_prb_1")
		self.label_p_2 = self.findChild(QLabel,"label_prb_2")
		self.label_p_3 = self.findChild(QLabel,"label_prb_3")
		self.label_p_4 = self.findChild(QLabel,"label_prb_4")
		self.label_p_5 = self.findChild(QLabel,"label_prb_5")
		self.label_p_6 = self.findChild(QLabel,"label_prb_6")
		self.label_p_7 = self.findChild(QLabel,"label_prb_7")
		self.label_p_8 = self.findChild(QLabel,"label_prb_8")
		self.label_p_9 = self.findChild(QLabel,"label_prb_9")
		self.label_p_10 = self.findChild(QLabel,"label_prb_10")
		self.label_p_11 = self.findChild(QLabel,"label_prb_11")
		self.label_p_12 = self.findChild(QLabel,"label_prb_12")
		self.label_p_13 = self.findChild(QLabel,"label_prb_13")
		self.label_p_14 = self.findChild(QLabel,"label_prb_14")
		self.label_p_15 = self.findChild(QLabel,"label_prb_15")
		self.label_p_16 = self.findChild(QLabel,"label_prb_16")
		self.label_p_17 = self.findChild(QLabel,"label_prb_17")
		self.label_p_18 = self.findChild(QLabel,"label_prb_18")
		self.label_p_19 = self.findChild(QLabel,"label_prb_19")
		self.label_p_20 = self.findChild(QLabel,"label_prb_20")
		self.label_p_21 = self.findChild(QLabel,"label_prb_21")
		self.label_p_22 = self.findChild(QLabel,"label_prb_22")
		self.label_p_23 = self.findChild(QLabel,"label_prb_23")
		self.label_p_24 = self.findChild(QLabel,"label_prb_24")
		self.label_p_25 = self.findChild(QLabel,"label_prb_25")
		self.label_p_26 = self.findChild(QLabel,"label_prb_26")
		self.label_p_27 = self.findChild(QLabel,"label_prb_27")
		self.label_p_28 = self.findChild(QLabel,"label_prb_28")
		self.label_p_29 = self.findChild(QLabel,"label_prb_29")
		self.label_p_30 = self.findChild(QLabel,"label_prb_30")
		self.label_p_31 = self.findChild(QLabel,"label_prb_31")
		self.label_p_32 = self.findChild(QLabel,"label_prb_32")
		#Modo de prueba - Labels de salida
		self.label_p_ax = self.findChild(QLabel,"label_prb_ax")
		self.label_p_ay = self.findChild(QLabel,"label_prb_ay")
		self.label_p_az = self.findChild(QLabel,"label_prb_az")
		self.label_p_fp_Gx = self.findChild(QLabel,"label_prb_fp_Gx")
		self.label_p_d_Gy = self.findChild(QLabel,"label_prb_delta_Gy")
		self.label_p_Gz = self.findChild(QLabel,"label_prb_Gz")
		self.label_p_Mx = self.findChild(QLabel,"label_prb_Mx")
		self.label_p_My = self.findChild(QLabel,"label_prb_My")
		self.label_p_Mz = self.findChild(QLabel,"label_prb_Mz")
		self.label_p_T = self.findChild(QLabel,"label_prb_T")
		self.label_p_vrF_rollNav = self.findChild(QLabel,"label_prb_vr_F_rollNav")
		self.label_p_vrR_pitchNav = self.findChild(QLabel,"label_prb_vr_R_pitchNav")
		self.label_p_vrL_yawNav = self.findChild(QLabel,"label_prb_vr_L_yawNav")
		self.label_p_v5r_velENav = self.findChild(QLabel,"label_prb_v5_r_velENav")
		self.label_p_velNNav = self.findChild(QLabel,"label_prb_velNNav")
		self.label_p_velUNav = self.findChild(QLabel,"label_prb_velUNav")
		self.label_p_LonNav = self.findChild(QLabel,"label_prb_LonNav")
		self.label_p_LatNav = self.findChild(QLabel,"label_prb_LatNav")
		self.label_p_altNav = self.findChild(QLabel,"label_prb_altNav")
		self.label_p_Hbar = self.findChild(QLabel,"label_prb_Hbar")
		self.label_p_Td_rollGPS = self.findChild(QLabel,"label_prb_Td_rollGPS")
		self.label_p_Ti_pitchGPS = self.findChild(QLabel,"label_prb_Ti_pitchGPS")
		self.label_p_B1_yawGPS = self.findChild(QLabel,"label_prb_B1_yawGPS")
		self.label_p_B2_velEGPS = self.findChild(QLabel,"label_prb_B2_velEGPS")
		self.label_p_velNGPS = self.findChild(QLabel,"label_prb_velNGPS")
		self.label_p_velUGPS = self.findChild(QLabel,"label_prb_velUGPS")
		self.label_p_LonGPS = self.findChild(QLabel,"label_prb_LonGPS")
		self.label_p_LatGPS = self.findChild(QLabel,"label_prb_LatGPS")
		self.label_p_AltGPS = self.findChild(QLabel,"label_prb_AltGPS")
		#Modo de prueba - Ocultar labels iniciales
		self.label_p_6.hide()
		self.label_p_7.hide()
		self.label_p_8.hide()
		self.label_p_9.hide()
		self.label_p_10.hide()
		self.label_p_15.hide()
		self.label_p_16.hide()
		self.label_p_17.hide()
		self.label_p_18.hide()
		self.label_p_19.hide()
		self.label_p_20.hide()
		self.label_p_25.hide()
		self.label_p_26.hide()
		self.label_p_27.hide()
		self.label_p_28.hide()
		self.label_p_29.hide()
		self.label_p_30.hide()
		#self.label_p_31.hide()
		self.label_p_32.hide()
		self.label_p_Gz.hide()
		self.label_p_Mx.hide()
		self.label_p_My.hide()
		self.label_p_Mz.hide()
		self.label_p_T.hide()
		self.label_p_velNNav.hide()
		self.label_p_velUNav.hide()
		self.label_p_LonNav.hide()
		self.label_p_LatNav.hide()
		self.label_p_altNav.hide()
		self.label_p_Hbar.hide()
		self.label_p_velNGPS.hide()
		self.label_p_velUGPS.hide()
		self.label_p_LonGPS.hide()
		self.label_p_LatGPS.hide()
		self.label_p_AltGPS.hide()

		self.label_p_31.setText('Sensores')
		self.combo_prueba.activated.connect(self.cambiar_disp_prueba)

		self.fre_widget_plot = self.findChild(PlotWidget,"fre_widget_plot")
		self.fre_widget_plot.setBackground('w')
		self.red_pen = mkPen(color=(255, 0, 0), width=2)

		self.show()

	@pyqtSlot()
	def tab_change(self):
		self.tab_index = self.tabs_pruebas.currentIndex()
		print(f'Current tab: {self.tab_index}')

	@pyqtSlot()
	def start_acquisition(self):
		print('Start acquisition')
		self.button_start.setEnabled(False)
		self.button_stop.setEnabled(True)
		self.combo_prueba.setEnabled(False)
		for index in (0,1,2,3,4):
			if index!=self.tab_index:
				self.tabs_pruebas.setTabEnabled(index,False)

		self.timer.setInterval(98)
		self.timer.timeout.connect(self.update_plot)
		self.timer.start()

		self.button_start.setEnabled(False)
		self.button_stop.setEnabled(True)

	@pyqtSlot()
	def stop_acquisition(self):
		print('Stop acquisition')
		self.timer.stop()

		self.button_start.setEnabled(True)
		self.button_stop.setEnabled(False)
		self.combo_prueba.setEnabled(True)

		for index in (0,1,2,3,4):
			self.tabs_pruebas.setTabEnabled(index,True)

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

	@pyqtSlot()
	def reiniciar_fase(self):
		self.fase_frenado = 0
		self.cambiar_fase()

	@pyqtSlot()
	def cambiar_disp_prueba(self):
		if self.combo_prueba.currentIndex()==0:
			self.label_p_4.setText('fp (N)')
			self.label_p_5.setText('δ (°)')
			self.label_p_11.setText('Vr_F (m/s)')
			self.label_p_12.setText('Vr_R (m/s)')
			self.label_p_13.setText('Vr_L (m/s)')
			self.label_p_14.setText('V5_r (m/s)')
			self.label_p_21.setText('Td (°C)')
			self.label_p_22.setText('Ti (°C)')
			self.label_p_23.setText('B1 (kg)')
			self.label_p_24.setText('B2 (kg)')
			self.label_p_31.setText('Sensores')

			self.label_p_6.hide()
			self.label_p_7.hide()
			self.label_p_8.hide()
			self.label_p_9.hide()
			self.label_p_10.hide()
			self.label_p_15.hide()
			self.label_p_16.hide()
			self.label_p_17.hide()
			self.label_p_18.hide()
			self.label_p_19.hide()
			self.label_p_20.hide()
			self.label_p_25.hide()
			self.label_p_26.hide()
			self.label_p_27.hide()
			self.label_p_28.hide()
			self.label_p_29.hide()
			self.label_p_30.hide()
			#self.label_p_31.hide()
			self.label_p_32.hide()
			self.label_p_Gz.hide()
			self.label_p_Mx.hide()
			self.label_p_My.hide()
			self.label_p_Mz.hide()
			self.label_p_T.hide()
			self.label_p_velNNav.hide()
			self.label_p_velUNav.hide()
			self.label_p_LonNav.hide()
			self.label_p_LatNav.hide()
			self.label_p_altNav.hide()
			self.label_p_Hbar.hide()
			self.label_p_velNGPS.hide()
			self.label_p_velUGPS.hide()
			self.label_p_LonGPS.hide()
			self.label_p_LatGPS.hide()
			self.label_p_AltGPS.hide()

		if self.combo_prueba.currentIndex()==1:
			self.label_p_4.setText('Gx (deg/s)')
			self.label_p_5.setText('Gy (deg/s)')
			self.label_p_11.setText('Roll (deg)')
			self.label_p_12.setText('Pitch (deg)')
			self.label_p_13.setText('Yaw (deg)')
			self.label_p_14.setText('Vel_E (m/s)')
			self.label_p_21.setText('Roll (deg)')
			self.label_p_22.setText('Pitch (deg)')
			self.label_p_23.setText('Yaw (deg)')
			self.label_p_24.setText('Vel_E (m/s)')
			self.label_p_31.setText('Navegación')

			self.label_p_6.show()
			self.label_p_7.show()
			self.label_p_8.show()
			self.label_p_9.show()
			self.label_p_10.show()
			self.label_p_15.show()
			self.label_p_16.show()
			self.label_p_17.show()
			self.label_p_18.show()
			self.label_p_19.show()
			self.label_p_20.show()
			self.label_p_25.show()
			self.label_p_26.show()
			self.label_p_27.show()
			self.label_p_28.show()
			self.label_p_29.show()
			self.label_p_30.show()
			#self.label_p_31.show()
			self.label_p_32.show()
			self.label_p_Gz.show()
			self.label_p_Mx.show()
			self.label_p_My.show()
			self.label_p_Mz.show()
			self.label_p_T.show()
			self.label_p_velNNav.show()
			self.label_p_velUNav.show()
			self.label_p_LonNav.show()
			self.label_p_LatNav.show()
			self.label_p_altNav.show()
			self.label_p_Hbar.show()
			self.label_p_velNGPS.show()
			self.label_p_velUGPS.show()
			self.label_p_LonGPS.show()
			self.label_p_LatGPS.show()
			self.label_p_AltGPS.show()

	def start_workers(self):
		serialPort1 = 'COM8' # Debe revisarse el puerto al que se conecta el GINS
		serialPort2 = 'COM9' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 38400
		
		self.thread[1] = MSerialPort(serialPort1,baudRate,parent=None,index=1)
		self.thread[1].start()
		self.thread[1].data.connect(self.update_labels)
		
		self.thread[2] = MSerialPort(serialPort2,baudRate,parent=None,index=2)
		self.thread[2].start()
		self.thread[2].data.connect(self.update_labels2)
		
	def stop_workers(self):
		self.thread[1].stop()
		self.thread[2].stop()
		#self.pushButton.setEnabled(True)

	# def start_aqcuisiton(self):
		
	# 	self.timer.setInterval(98)
	# 	self.timer.timeout.connect(self.update_plot)
	# 	self.timer.start()

	# 	self.button_start.setEnabled(False)
	# 	self.button_stop.setEnabled(True)
		
		# self.thread[3] = MAcquisiton(parent=None,index=3)
		# self.thread[3].start()
		# self.thread[3].data.connect(self.show_data)
		
		# self.thread[1].data.connect(self.thread[3].update_val1)
		# self.thread[2].data.connect(self.thread[3].update_val2)
		
		#self.pushButton_3.setEnabled(False)
		
	# def stop_aqcuisiton(self):
	# 	self.thread[3].stop()
	# 	self.button_start.setEnabled(True)
	# 	self.button_stop.setEnabled(False)
	
	def pause_resume_aqcuisiton(self):
		self.pause = not self.pause
		if self.pause:
			self.thread[3].pause()
			self.button_pause.setText("Resume")
		else:
			self.thread[3].resume()
			self.button_pause.setText("Pause")
	
	def update_labels(self,data):
		self.val1 = data
	
	def update_labels2(self,data):
		self.val2 = data

	def update_plot(self):
		#print(f'Print labels: {val}')
		self.t += 0.1
		val = [round(self.t,2)] + self.val1 + self.val2
		if self.tabs_pruebas.currentIndex()==0: #Prueba de frenado
			if self.fase_frenado==1:
				self.label_f_vx.setText(f'{val[1]}')
				self.label_f_ax.setText(f'{val[2]}')
				self.label_f_fp.setText(f'{val[3]}')
				if val[0]>0:
					self.line1.clear()
				if len(self.xdata)>=15:
					del self.xdata[0]
					del self.ydata[0]
				self.xdata.append(val[0])
				self.ydata.append(val[1])
				self.line1 = self.fre_widget_plot.plot(self.xdata,self.ydata,pen=self.red_pen,symbol='+', symbolSize=10, symbolBrush=('b'))
			elif self.fase_frenado==2:
				self.label_f_vx.setText(f'{val[4]}')
				self.label_f_ax.setText(f'{val[5]}')
				self.label_f_fp.setText(f'{val[6]}')
			elif self.fase_frenado==3:
				self.label_f_vx.setText(f'{val[1]}')
				self.label_f_ax.setText(f'{val[2]}')
				self.label_f_fp.setText(f'{val[3]}')
			elif self.fase_frenado==4:
				self.label_f_vx.setText(f'{val[4]}')
				self.label_f_ax.setText(f'{val[5]}')
				self.label_f_fp.setText(f'{val[6]}')
			elif self.fase_frenado==5:
				self.label_f_vx.setText(f'{val[1]}')
				self.label_f_ax.setText(f'{val[2]}')
				self.label_f_fp.setText(f'{val[3]}')
		if self.tabs_pruebas.currentIndex()==1: #Prueba de estabilidad
			self.label_e_vx.setText(f'{val[1]}')
			self.label_e_ay.setText(f'{val[2]}')
			self.label_e_delta.setText(f'{val[3]}')
			self.label_e_beta.setText(f'{val[4]}')
			self.label_e_phi.setText(f'{val[5]}')
		if self.tabs_pruebas.currentIndex()==2: #Prueba de vibraciones
			self.label_v_ax.setText(f'{val[1]}')
			self.label_v_ay.setText(f'{val[3]}')
			self.label_v_az.setText(f'{val[5]}')
		if self.tabs_pruebas.currentIndex()==4: #Modo de prueba
			if self.combo_prueba.currentIndex()==0:
				self.label_p_ax.setText(f'{val[1]}')
				self.label_p_ay.setText(f'{val[2]}')
				self.label_p_az.setText(f'{val[3]}')
			else:
				self.label_p_ax.setText(f'{val[4]}')
				self.label_p_ay.setText(f'{val[5]}')
				self.label_p_az.setText(f'{val[6]}')
		# if val[0]>0:
		# 	self.line1.clear()
		# if len(self.xdata)>=15:
		# 	del self.xdata[0]
		# 	del self.ydata[0]
		# self.xdata.append(val[0])
		# self.ydata.append(val[1])
		# self.line1 = self.plot_widget.plot(self.xdata,self.ydata,pen=self.red_pen,symbol='+', symbolSize=20, symbolBrush=('b'))


class MSerialPort(QThread):
	finished = pyqtSignal()
	data = pyqtSignal(list)
	def __init__(self,port,baud,parent=None,index=0):
		super(MSerialPort,self).__init__(parent)
		self.is_running = True
		self.is_paused = False
		self.index = index
		self.message = []
		self.port=serial.Serial(port,baud)
		self.port_open()
	def port_open(self):
		if not self.port.isOpen():
			self.port.open()
	def port_close(self):
		self.port.close()
	def flush(self):
		self.port.flushInput()
		self.port.flushOutput()
	def send_data(self,data):
		number=self.port.write(data)
		return number
	def run(self):
		self.port_open()
		while True:
			time.sleep(0.005)
			if self.is_paused:
				continue
			if not self.is_running:
				break
			try:
				data1 = self.port.readline().decode('ascii')
				data1 = data1.replace("[","").replace("]","").replace("\r\n","")
				self.message = list(map(float, data1.split(",")))
				#print(data1)
			except Exception as e:
				continue
				#print(e)
			self.data.emit(self.message)
			self.port.flushOutput()
	
	def pause(self):
		self.is_paused = True
		print(f'Tarea pausada en hilo {self.index}')

	def resume(self):
		self.is_paused = False
		print(f'Tarea continuada en hilo {self.index}')

	def stop(self):
		self.is_running = False
		print(f'Tarea terminada en hilo {self.index}')
		#self.finished.emit()
		self.port_close()
		self.terminate()


class MAcquisiton(QThread):
	finished = pyqtSignal()
	data = pyqtSignal(list)
	def __init__(self,val1=None,val2=None,parent=None,index=0):
		super(MAcquisiton,self).__init__(parent)
		self.is_running = True
		self.is_paused = False
		self.index = index
		if val1 is None:
			self.val1 = []
		else:
			self.val1 = val1
		if val2 is None:
			self.val2 = []
		else:
			self.val2 = val2
	def update_val1(self,val1):
		self.val1=val1
	def update_val2(self,val2):
		self.val2=val2
	def run(self):
		time.sleep(5) #Wait to refresh vals
		t = 0
		while True:
			time.sleep(0.05)
			if self.is_paused:
				continue
			if not self.is_running:
				break
			self.data.emit([round(t,2)]+self.val1+self.val2)
			t += 0.05
	
	def pause(self):
		self.is_paused = True
		print(f'Tarea pausada en hilo {self.index}')

	def resume(self):
		self.is_paused = False
		print(f'Tarea continuada en hilo {self.index}')

	def stop(self):
		self.is_running = False
		print(f'Tarea terminada en hilo {self.index}')
		#self.finished.emit()
		self.terminate()


if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	win = UI()
	win.show()
	sys.exit(app.exec())