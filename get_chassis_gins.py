# Pruebas de conexión con el chasis NI
# Pruebas de adquisición de datos de varios canales - Chasís NI
# Comunicación serial - GINS200

import nidaqmx as daq
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import time
from numpy import rint
#import matplotlib.pyplot as plt
import serial
import threading
import sqlite3
from bitstring import BitArray

def main(args):

	serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
	baudRate = 460800

	print('Inicio')
	## GINS200=serial('COM5','BaudRate',460800,'Parity','none','DataBits',8,'StopBits',1,'Terminator','CR')
	#mSerial_gins=serial.Serial(serialPort,baudRate,bytesize=serial.EIGHTBITS, 
	#	parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
	mSerial_gins = MSerialPort(serialPort,baudRate)
	mSerial_gins.flush()

	db_Name = "pruebaDB.db"
	db_Table = "Variables_Chassis_Gins"
	db1 = Database(db_Name,db_Table)

	print('Conectado')
		
	t1 = threading.Thread(target = mSerial_gins.read_data)
	t1.start()
	#t2 = threading.Thread(target = mSerial2.read_data)
	#t2.start()
	time.sleep(2)

	print('---------------------------')
	for i in range(0,100):
		time.sleep(0.01)
		
		data1 = mSerial_gins.message
		print(f'Dato GINS: {data1}')
		
		
		#db1.save_data(data1+data2)
		print('---------------------------')

	mSerial_gins.read_flag = True
	mSerial_gins.port_close()
	print('Puertos cerrados!')
	t1.join()
	print('Hilos finalizados!')

def save_db(db_name,db_table):
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
def get_gins_values(data):
	#data = str(hex(int(BitArray(in_stream).bin,2)))
	start_data = data.find('aa550364')
	out_stream = data[start_data:start_data+200]
	print(out_stream)
	
	# Get values from separated bytes
	sens_gyro = 1e-4 #Gyro sens
	sens_acc = 1e-5 #Acc sens
	sens_magn = 1e-2 #Magn sens
	sens_hbar = 1e-2 #Hbar sens
	gyro_x = sens_gyro*float(hex2sint(out_stream[8:14],3))
	gyro_y = sens_gyro*float(hex2sint(out_stream[14:20],3))
	gyro_z = sens_gyro*float(hex2sint(out_stream[20:26],3))
	#print(f'[gyro_x,gyro_y,gyro_z]: [{gyro_x},{gyro_y},{gyro_z}]')
	acc_x = sens_acc*float(hex2sint(out_stream[26:32],3))
	acc_y = sens_acc*float(hex2sint(out_stream[32:38],3))
	acc_z = sens_acc*float(hex2sint(out_stream[38:44],3))
	#print(f'[acc_x,acc_y,acc_z]: [{acc_x},{acc_y},{acc_z}]')
	magn_x = sens_magn*float(hex2sint(out_stream[44:48],2))
	magn_y = sens_magn*float(hex2sint(out_stream[48:52],2))
	magn_z = sens_magn*float(hex2sint(out_stream[52:56],2))
	#print(f'[magn_x,magn_y,magn_z]: [{magn_x},{magn_y},{magn_z}]')
	h_bar = sens_hbar*float(hex2sint(out_stream[56:62],3))
	#acc_y = sens_acc*float(hex2sint(out_stream[32:38],3))
	#print(f'[h_bar]: [{h_bar}]')

	return [round(v,5) for v in [gyro_x,gyro_y,gyro_z,acc_x,acc_y,acc_z,magn_x,magn_y,magn_z,h_bar]]
	
def hex2sint(val,num_bytes):
	sign = False
	if num_bytes==3:
		bin_data = "{0:024b}".format(int(val, 16))
	elif num_bytes==2:
		bin_data = "{0:016b}".format(int(val, 16))
	else:
		return None #No devuelve nada si el dato no tiene 2 o 3 bytes
	return BitArray(bin=bin_data).int

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
	message=''
	read_flag = False
	def __init__(self,port,baud):
		self.port=serial.Serial(port,baud,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1) #Para el GINS200
		if not self.port.isOpen():
			self.port.open()
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
				datoS = get_gins_values(out.hex())
				print(f'DatoS = {datoS}')
				self.message = datoS
			if self.read_flag:
				self.read_flag = False
				break


if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
