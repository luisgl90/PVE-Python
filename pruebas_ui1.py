# Pruebas de conexión con el chasis NI
# Pruebas de adquisición de datos de varios canales - Chasís NI
# Comunicación serial - GINS200

import nidaqmx as daq
import math
import time
#import numpy 
#import matplotlib.pyplot as plt
import sqlite3
import threading
import serial
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
from bitstring import BitArray
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel,QComboBox,QTabWidget
from PyQt5.QtCore import pyqtSlot,QTimer,Qt,QObject, QThread, pyqtSignal
from PyQt5 import uic

class UI(QMainWindow):

	s = pyqtSignal(dict)

	def __init__(self, parent=None):
		super(UI,self).__init__(parent)
		self.main() #Inicializa las variables y objetos
    
		self.cdaq_data = []
		self.gins_data = {}

		uic.loadUi("interfaz_app.ui",self)
		
		self.fase_frenado = 1
		self.fases_frenado = ['Eficiencia en frío','Calentamiento','Eficiencia en caliente',
			'Recuperación','Eficiencia de recuperación']
		
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

		self.show()

	def main(self):

		#serialPort = '/dev/ttyUSB0' 
		#serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
		#baudRate = 460800

		print('Inicio')
		## GINS200=serial('COM5','BaudRate',460800,'Parity','none','DataBits',8,'StopBits',1,'Terminator','CR')
		#mSerial_gins=serial.Serial(serialPort,baudRate,bytesize=serial.EIGHTBITS, 
		#	parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
		#self.mSerial_gins = MSerialPort(serialPort,baudRate) # Objeto para conexión serial con el GINS200
		#self.mSerial_gins.flush()

		#self.cdaq1 = task_cdaq() #Objeto para el chasís
		
		self.db_Name = "pruebaDB.db"
		self.db_Table = "Variables_Chassis_Gins"
		self.db1 = Database(self.db_Name,self.db_Table)

		print('Conectado')
			
		#self.t1 = threading.Thread(target = self.mSerial_gins.read_data)
		#self.t1.start()
		#self.t2 = threading.Thread(target = self.cdaq1.read_data)
		#self.t2.start()
		#self.t3 = threading.Thread(target = self.acquisition_main)
		#self.t3.start()
		#time.sleep(3) #Espera mientras se configuran los puertos para cDAQ y GINS

	def acquisition_main(self):
		#self.data = Signal(dict)
		self.thread = QThread()
		serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 460800
		self.mSerial_gins = MSerialPort(serialPort,baudRate) # Objeto para conexión serial con el GINS200
		self.cdaq1 = task_cdaq() #Objeto para el chasís
		self.cdaq1.moveToThread(self.thread)
		self.mSerial_gins.moveToThread(self.thread)
		self.thread.started.connect(self.mSerial_gins.read_data)
		self.thread.started.connect(self.cdaq1.read_data)
		
		self.s.connect(self.update_labels_gins)

		self.thread.start()

		print('---------------------------')
		print('-----Inicia adquisición-----')
		print('---------------------------')
		#time.sleep(3) #Espera mientras se configuran los puertos para cDAQ y GINS
		
		#timer = QTimer()
		#timer.timeout.connect(self.update_labels)
		#timer.start(50)  # every 10,000 milliseconds
		
		#for i in range(0,50):
		#	time.sleep(0.05)
		#	self.cdaq_data = self.cdaq1.data
		#	self.gins_data = self.mSerial_gins.message
		#	#self.s.emit(self.gins_data)
		#	print(f'Dato[{i}] cDAQ: {self.cdaq_data}')
		#	print(f'Dato[{i}] GINS: {self.gins_data}')
			
		#print('-----------Fin Acq----------------')

	def update_labels_gins(self,data):
		self.label_p_ax.setText(str(data["acc_x"]))
		self.label_p_ay.setText(str(data["acc_y"]))
		self.label_p_az.setText(str(data["acc_z"]))
		self.label_p_fp_Gx.setText(str(data["gyro_x"]))
		self.label_p_d_Gy.setText(str(data["gyro_y"]))
		self.label_p_Gz.setText(str(data["gyro_z"]))
		self.label_p_Mx.setText(str(data["magn_x"]))
		self.label_p_My.setText(str(data["magn_y"]))
		self.label_p_Mz.setText(str(data["magn_z"]))
		self.label_p_T.setText(str(data["T"]))
		self.label_p_vrF_rollNav.setText(str(data["nav_roll"]))
		self.label_p_vrR_pitchNav.setText(str(data["nav_pitch"]))
		self.label_p_vrL_yawNav.setText(str(data["nav_yaw"]))
		self.label_p_v5r_velENav.setText(str(data["nav_vel_E"]))
		self.label_p_velNNav.setText(str(data["nav_vel_N"]))
		self.label_p_velUNav.setText(str(data["nav_vel_U"]))
		self.label_p_LonNav.setText(str(data["nav_Lon"]))
		self.label_p_LatNav.setText(str(data["nav_Lat"]))
		self.label_p_altNav.setText(str(data["nav_alt"]))
		self.label_p_Hbar.setText(str(data["h_bar"]))
		#self.label_p_Td_rollGPS.setText(str(self.gins_data["gps_roll"]))
		#self.label_p_Ti_pitchGPS.setText(str(self.gins_data["gps_pitch"]))
		self.label_p_B1_yawGPS.setText(str(data["gps_yaw"]))
		self.label_p_B2_velEGPS.setText(str(data["gps_vel_E"]))
		self.label_p_velNGPS.setText(str(data["gps_vel_N"]))
		self.label_p_velUGPS.setText(str(data["gps_vel_U"]))
		self.label_p_LonGPS.setText(str(data["gps_Lon"]))
		self.label_p_LatGPS.setText(str(data["gps_Lat"]))
		self.label_p_AltGPS.setText(str(data["gps_alt"]))

	def save_db(self,db_name,db_table):
		db_conn = None

		try:
			db_conn = sqlite3.connect("database/" + db_name)
			cursor = db_conn.cursor()
			cursor.execute("CREATE TABLE IF NOT EXISTS " + db_table + " (t REAL NOT NULL, Dist REAL NOT NULL, Fp REAL NOT NULL, Vx REAL NOT NULL, Vy REAL NOT NULL, Vz REAL NOT NULL, Ax REAL NOT NULL, Ay REAL NOT NULL, Az REAL NOT NULL, Ti REAL NOT NULL, Td REAL NOT NULL, PRIMARY KEY (t))")
			
			cursor.execute("INSERT INTO " + db_table + "(t, Dist, Fp, Vx, Vy, Vz, Ax, Ay, Az, Ti, Td) VALUES(?,?,?,?,?,?,?,?,?,?,?)",tuple(data))
			db_conn.commit()
			
		except Exception as ex:
			print(ex)

	# Se agregaron las funciones para tomar y convertir datos del GINS200
	@pyqtSlot()
	def tab_change(self):
		self.tab_index = self.tabs_pruebas.currentIndex()
		print(f'Current tab: {self.tab_index}')

	@pyqtSlot()
	def start_acquisition(self):
		self.flag_acq = True
		print('Start acquisition')
		self.button_start.setEnabled(False)
		self.button_stop.setEnabled(True)
		self.combo_prueba.setEnabled(False)
		for index in (0,1,2,3,4):
			if index!=self.tab_index:
				self.tabs_pruebas.setTabEnabled(index,False)
		self.acquisition_main()

	@pyqtSlot()
	def stop_acquisition(self):
		print('Stop acquisition')
		self.button_start.setEnabled(True)
		self.button_stop.setEnabled(False)
		self.combo_prueba.setEnabled(True)
		for index in (0,1,2,3,4):
			self.tabs_pruebas.setTabEnabled(index,True)
		self.flag_acq = False
		self.t3.join()

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

class Database:
	db_conn = None
	db_flag = False #Aún sin uso
	def __init__(self,db_name,db_table):
		try:
			self.db_name = db_name
			self.db_table = db_table
			self.db_conn = sqlite3.connect("database/" + db_name)
			self.cursor = self.db_conn.cursor()
			
		except Exception as ex:
			print(ex)
	def save_data(self,data):
		try:
			self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.db_table + " (n REAL , v1 REAL NOT NULL, v2 REAL NOT NULL, v3 REAL NOT NULL, v4 REAL NOT NULL, v5 REAL NOT NULL,v6 REAL NOT NULL, v7 REAL NOT NULL, PRIMARY KEY (n))")
			self.cursor.execute("INSERT INTO " + self.db_table + "(v1,v2,v3,v4,v5,v6,v7) VALUES(?,?,?,?,?,?,?)",tuple(data))
			self.db_conn.commit()
		except Exception as ex:
			print(ex)
	def conn_close(self):
		self.db_conn.close()


class MSerialPort(QObject):
	vals = dict()
	message = None
	read_flag = False
	def __init__(self,port,baud):
		super(MSerialPort, self).__init__()
		self.port=serial.Serial(port,baud,bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1) #Para el GINS200
		if not self.port.isOpen():
			self.port.open()
		self.flush()
	def port_open(self):
		if not self.port.isOpen():
			self.port.open()
	def port_close(self):
		self.port.close()
	def send_data(self,data):
		number=self.port.write(data)
		return number
	def flush(self):
		self.port.flushInput()
		self.port.flushOutput()
	def read_data(self):
		print("GINS iniciado en hilo!")
		while True:
			out = ''
			while self.port.inWaiting() > 0: 
				out = self.port.read(self.port.inWaiting())#.decode('uint8')
			if out != '':
				#datoS = get_gins_values(out.hex())
				#print(f'DatoS = {datoS}')
				#self.message = datoS
				self.message = self.get_gins_values(out.hex())
			if self.read_flag:
				self.read_flag = False
				break
	def get_gins_values(self,data):
		try:
			#data = str(hex(int(BitArray(in_stream).bin,2)))
			start_data = data.find('aa550364')
			out_stream = data[start_data:start_data+200]
			#print(out_stream)
			
			# Get values from separated bytes
			sens_gyro = 1e-4 #Gyro sens
			sens_acc = 1e-5 #Acc sens
			sens_magn = 1e-2 #Magn sens
			sens_hbar = 1e-2 #Hbar sens
			sens_att = 1e-2 #Att sens
			sens_vel = 1e-4 #Vel sens
			sens_lon_lat = 1e-7 #Lon and Lat sens
			sens_alt = 1e-2 # Alt sens
			sens_T = 1e-2 # Temp sens

			self.vals["gyro_x"] = sens_gyro*float(self.hex2sint(out_stream[8:14],3))
			self.vals["gyro_y"] = sens_gyro*float(self.hex2sint(out_stream[14:20],3))
			self.vals["gyro_z"] = sens_gyro*float(self.hex2sint(out_stream[20:26],3))
			#print(f'[gyro_x,gyro_y,gyro_z]: [{gyro_x},{gyro_y},{gyro_z}]')
			self.vals["acc_x"] = sens_acc*float(self.hex2sint(out_stream[26:32],3))
			self.vals["acc_y"] = sens_acc*float(self.hex2sint(out_stream[32:38],3))
			self.vals["acc_z"] = sens_acc*float(self.hex2sint(out_stream[38:44],3))
			#print(f'[acc_x,acc_y,acc_z]: [{acc_x},{acc_y},{acc_z}]')
			self.vals["magn_x"] = sens_magn*float(self.hex2sint(out_stream[44:48],2))
			self.vals["magn_y"] = sens_magn*float(self.hex2sint(out_stream[48:52],2))
			self.vals["magn_z"] = sens_magn*float(self.hex2sint(out_stream[52:56],2))
			#print(f'[magn_x,magn_y,magn_z]: [{magn_x},{magn_y},{magn_z}]')
			self.vals["h_bar"] = sens_hbar*float(self.hex2sint(out_stream[56:62],3))
						
			self.vals["gps_vel_E"] = sens_vel*float(self.hex2sint(out_stream[80:86],3))
			self.vals["gps_vel_N"] = sens_vel*float(self.hex2sint(out_stream[86:92],3))
			self.vals["gps_vel_U"] = sens_vel*float(self.hex2sint(out_stream[92:98],3))
			
			self.vals["gps_Lon"] = sens_lon_lat*float(self.hex2sint(out_stream[98:106],4))
			self.vals["gps_Lat"] = sens_lon_lat*float(self.hex2sint(out_stream[106:114],4))
			self.vals["gps_alt"] = sens_alt*float(self.hex2sint(out_stream[114:120],3))
			self.vals["gps_yaw"] = sens_att*float(self.hex2sint(out_stream[120:124],2))
			
			self.vals["nav_pitch"] = sens_att*float(self.hex2sint(out_stream[130:134],2))
			self.vals["nav_roll"] = sens_att*float(self.hex2sint(out_stream[134:138],2))
			self.vals["nav_yaw"] = sens_att*float(self.hex2sint(out_stream[138:142],2)) #Unsigned
			#print(f'[pitch,roll,yaw]: [{ang_pitch},{ang_roll},{ang_yaw}]')
			self.vals["nav_vel_E"] = sens_vel*float(self.hex2sint(out_stream[142:148],3))
			self.vals["nav_vel_N"] = sens_vel*float(self.hex2sint(out_stream[148:154],3))
			self.vals["nav_vel_U"] = sens_vel*float(self.hex2sint(out_stream[154:160],3))
			#print(f'[vel_E,vel_N]: [{vel_E},{vel_N}]')
			self.vals["nav_Lon"] = sens_lon_lat*float(self.hex2sint(out_stream[160:168],4))
			self.vals["nav_Lat"] = sens_lon_lat*float(self.hex2sint(out_stream[168:176],4))
			self.vals["nav_alt"] = sens_alt*float(self.hex2sint(out_stream[176:182],3))
			
			self.vals["T"] = sens_T*float(self.hex2sint(out_stream[192:196],2))

			return self.vals # Retorna un diccionario con todas las mediciones
		except Exception as ex:
			#print(ex)
			return self.vals

	def hex2sint(self,val,num_bytes):
		if num_bytes==4:	# Dato de 4 bytes / 32 bits
			bin_data = "{0:032b}".format(int(val, 16))
		elif num_bytes==3:	# Dato de 3 bytes / 24 bits
			bin_data = "{0:024b}".format(int(val, 16))
		elif num_bytes==2:	# Dato de 2 bytes / 16 bits
			bin_data = "{0:016b}".format(int(val, 16))
		return BitArray(bin=bin_data).int

	#def hex2uint(self,val,num_bytes):
	#	return int(val,8*num_bytes)

class task_cdaq(QObject):
	task1 = None
	task2 = None
	task3 = None
	data=''
	read_flag = False
	devC = nidaqmx.system.device.Device('cDAQ9188')
	devC.reserve_network_device(True)
	min_V = -10
	max_V = 10

	def __init__(self):
		super(task_cdaq, self).__init__()
		self.task1 = nidaqmx.Task() 
		self.task2 = nidaqmx.Task()
		self.task3 = nidaqmx.Task()

		#Config módulo 7
		self.task1.ai_channels.add_ai_bridge_chan("cDAQ9188Mod7/ai0",name_to_assign_to_channel='c7_0',
			bridge_config=nidaqmx.constants.BridgeConfiguration.FULL_BRIDGE,
			nominal_bridge_resistance=700.0)	#Pedal
		#print(c7_0)
		#print(c7_0.ai_meas_type)
		#Config módulo 2
		self.task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai0",name_to_assign_to_channel='c2_0',
			min_val=self.min_V,max_val=self.max_V)	#Temp der
		#print(c2_0)
		#c2_0.ai_meas_type = nidaqmx.constants.UsageTypeAI.VOLTAGE
		self.task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai1",name_to_assign_to_channel='c2_1',
			min_val=self.min_V,max_val=self.max_V)	#Temp izq
		#print(c2_1)
		#c2_1.ai_meas_type = nidaqmx.constants.UsageTypeAI.VOLTAGE
		self.task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai2",min_val=self.min_V,max_val=self.max_V)	#Rueda delantera
		
		#Config módulo 3
		self.task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai0",min_val=self.min_V,max_val=self.max_V)	#5ta rueda
		self.task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai1",min_val=self.min_V,max_val=self.max_V)	#Rueda izq
		self.task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai2",min_val=self.min_V,max_val=self.max_V)	#Rueda der
		self.task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai3",min_val=self.min_V,max_val=self.max_V)	#Volante
		
		#Config módulo 8
		#sensX=99.07e-3	#mV/g	10.10e-3; %V/ms-2  
		#sensY=97.08e-3	#mV/g	9.89e-3; %V/ms-2   
		#sensZ=101.7e-3	#mV/g	10.38e-3; %V/ms-2 
		sensX=99.07e-6	#V/g
		sensY=97.08e-6	#V/g
		sensZ=101.7e-6	#V/g
		self.task3.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai0",
			units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
			sensitivity=sensX, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc x
		self.task3.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai1",
			units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
			sensitivity=sensY, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc y
		self.task3.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai2",
			units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
			sensitivity=sensZ, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc z
		
		self.task1.timing.cfg_samp_clk_timing(rate=1000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
		self.task2.timing.cfg_samp_clk_timing(rate=1000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
		self.task3.timing.cfg_samp_clk_timing(rate=1000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
	def close(self):
		self.task.close()
	def list2dict(self,data):
		res = dict() #'[fp,Td,Ti,Rdel,5aR,Rder,Rizq,Vol,AccX,AccY,AccZ]'
		res["fp"] = float(data[0])
		res["Td"] = float(data[1][0])
		res["Ti"] = float(data[2][0])
		res["Rdel"] = float(data[3][0])
		res["5aR"] = float(data[4][0])
		res["Rder"] = float(data[5][0])
		res["Rizq"] = float(data[6][0])
		res["Vol"] = float(data[7][0])
		res["AccX"] = float(data[8][0])
		res["AccY"] = float(data[9][0])
		res["AccZ"] = float(data[10][0])
		return res
	def read_data(self):
		print("Tarea cDAQ iniciada en hilo!")
		while True:
			self.data = self.list2dict(self.task1.read(number_of_samples_per_channel=1) + self.task2.read(number_of_samples_per_channel=1) + self.task3.read(number_of_samples_per_channel=1))
			print(self.data)
			if self.read_flag:
				self.read_flag = False
				break

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	UIWindow = UI()
	app.exec_()
	#sys.exit(main(sys.argv))
	
