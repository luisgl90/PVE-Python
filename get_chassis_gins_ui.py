# Pruebas de conexión con el chasis NI
# Pruebas de adquisición de datos de varios canales - Chasís NI
# Comunicación serial - GINS200

#import nidaqmx as daq
import math
import time
#import numpy 
#import matplotlib.pyplot as plt
import sqlite3
import threading
import serial
import nidaqmx
#from nidaqmx.constants import TerminalConfiguration
from bitstring import BitArray
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QPushButton, QLabel
from PyQt5 import uic


class UI(QDialog):
	def __init__(self):
		super(UI,self).__init__()
		self.main() #Inicializa las variables y objetos
		uic.loadUi('interfaz_estabilidad1.ui',self) #Carga la interfaz hecha con Designer
		
		self.labelv = self.findChild(QLabel,"label_v")
		self.labelax = self.findChild(QLabel,"label_ax")
		self.labeldh = self.findChild(QLabel,"label_dh")
		
		self.show()

	def main(self):
		
		serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 460800

		print('Inicio')
		## GINS200=serial('COM5','BaudRate',460800,'Parity','none','DataBits',8,'StopBits',1,'Terminator','CR')
		#mSerial_gins=serial.Serial(serialPort,baudRate,bytesize=serial.EIGHTBITS, 
		#	parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
		self.mSerial_gins = MSerialPort(serialPort,baudRate) # Objeto para conexión serial con el GINS200
		self.mSerial_gins.flush()

		self.cdaq1 = task_cdaq() #Objeto para el chasís
		
		self.db_Name = "pruebaDB.db"
		self.db_Table = "Variables_Chassis_Gins"
		self.db1 = Database(self.db_Name,self.db_Table)

		print('Conectado')
			
		self.t1 = threading.Thread(target = self.mSerial_gins.read_data)
		self.t1.start()
		self.t2 = threading.Thread(target = self.cdaq1.read_data)
		self.t2.start()
		self.t3 = threading.Thread(target = self.acquisition_main)
		self.t3.start()

	def acquisition_main(self):
		print('---------------------------')
		print('-----Inicia adquisición-----')
		print('---------------------------')
		time.sleep(3) #Espera mientras se configuran los puertos para cDAQ y GINS
		for i in range(0,200):
			time.sleep(0.1)
			self.cdaq_data = [round(v,3) for v in self.cdaq1.data]
			self.gins_data = self.mSerial_gins.message
			print(f'Dato[{i}] cDAQ: {self.cdaq_data}')
			print(f'Dato[{i}] GINS: {self.gins_data}')

			try:
				#[gyro_z,acc_x,vel_E,vel_N,roll,yaw]
				v = math.sqrt(pow(self.gins_data[2],2) + pow(self.gins_data[3],2))
				#v = self.cdaq_data
				self.labelv.setText(f'{v}')
				self.labelax.setText(f'{self.gins_data[1]}')
			except:
				self.labelv.setText('0.000')
				self.labelax.setText('0.000')
			self.labeldh.setText(f'{self.cdaq_data[1]}')
			print('---------------------------')

		self.mSerial_gins.read_flag = True
		self.mSerial_gins.port_close()
		self.cdaq1.read_flag = True
		self.cdaq1.close()
		print('Puertos cerrados!')
		self.t1.join()
		self.t2.join()
		#self.t3.join()
		print('Hilos finalizados!')


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


class MSerialPort:
	vals = []
	message=''
	read_flag = False
	def __init__(self,port,baud):
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
		print("Hilo iniciado!")
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
			gyro_x = sens_gyro*float(self.hex2sint(out_stream[8:14],3))
			gyro_y = sens_gyro*float(self.hex2sint(out_stream[14:20],3))
			gyro_z = sens_gyro*float(self.hex2sint(out_stream[20:26],3))
			#print(f'[gyro_x,gyro_y,gyro_z]: [{gyro_x},{gyro_y},{gyro_z}]')
			acc_x = sens_acc*float(self.hex2sint(out_stream[26:32],3))
			acc_y = sens_acc*float(self.hex2sint(out_stream[32:38],3))
			acc_z = sens_acc*float(self.hex2sint(out_stream[38:44],3))
			#print(f'[acc_x,acc_y,acc_z]: [{acc_x},{acc_y},{acc_z}]')
			magn_x = sens_magn*float(self.hex2sint(out_stream[44:48],2))
			magn_y = sens_magn*float(self.hex2sint(out_stream[48:52],2))
			magn_z = sens_magn*float(self.hex2sint(out_stream[52:56],2))
			#print(f'[magn_x,magn_y,magn_z]: [{magn_x},{magn_y},{magn_z}]')
			h_bar = sens_hbar*float(self.hex2sint(out_stream[56:62],3))
			#print(f'[h_bar]: [{h_bar}]')
			#acc_y = sens_acc*float(hex2sint(out_stream[32:38],3))
			ang_pitch = sens_att*float(self.hex2sint(out_stream[130:134],2))
			ang_roll = sens_att*float(self.hex2sint(out_stream[134:138],2))
			ang_yaw = sens_att*float(self.hex2uint(out_stream[138:142],2))
			#print(f'[pitch,roll,yaw]: [{ang_pitch},{ang_roll},{ang_yaw}]')
			vel_E = sens_vel*float(self.hex2sint(out_stream[142:148],3))
			vel_N = sens_vel*float(self.hex2sint(out_stream[148:154],3))
			#print(f'[vel_E,vel_N]: [{vel_E},{vel_N}]')
			#self.vals = [round(v,3) for v in [gyro_x,gyro_y,gyro_z,acc_x,acc_y,acc_z,magn_x,magn_y,magn_z,h_bar]]
			self.vals = [round(v,3) for v in [gyro_z,acc_x,vel_E,vel_N,ang_roll,ang_yaw]]
			return self.vals
		except:
			return self.vals

	def hex2sint(self,val,num_bytes):
		sign = False
		if num_bytes==3:
			bin_data = "{0:024b}".format(int(val, 16))
		elif num_bytes==2:
			bin_data = "{0:016b}".format(int(val, 16))
		else:
			return None #No devuelve nada si el dato no tiene 2 o 3 bytes
		return BitArray(bin=bin_data).int

	def hex2uint(self,val,num_bytes):
		return int(val,8*num_bytes)

class task_cdaq:
	task = None
	data=''
	read_flag = False
	def __init__(self):
		self.task = nidaqmx.Task()
		self.task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai2")
		self.task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai3")
		self.task.timing.cfg_samp_clk_timing(rate=100,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
	def close(self):
		self.task.close()
	def read_data(self):
		print("Tarea cDAQ iniciada en hilo!")
		while True:
			self.data = self.task.read()
			if self.read_flag:
				self.read_flag = False
				break

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	UIWindow = UI()
	app.exec_()
	#sys.exit(main(sys.argv))
	
