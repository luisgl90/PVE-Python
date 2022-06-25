# Pruebas de conexión con el chasis NI
# Pruebas de adquisición de datos de varios canales - Chasís NI
# Comunicación serial - GINS200

#import nidaqmx as daq
#import nidaqmx
#from nidaqmx.constants import TerminalConfiguration
import time
from numpy import rint
#import matplotlib.pyplot as plt
import serial
import threading
import sqlite3

def main(args):

	#serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
	#baudRate = 460800
	serialPort1 = 'COM8' # Debe revisarse el puerto al que se conecta el GINS
	serialPort2 = 'COM9' # Debe revisarse el puerto al que se conecta el GINS
	baudRate1 = 9600

	print('Inicio')
	## GINS200=serial('COM5','BaudRate',460800,'Parity','none','DataBits',8,'StopBits',1,'Terminator','CR')
	mSerial1=MSerialPort(serialPort1,baudRate1)#, parity='PARITY_NONE', bytesize='EIGHTBITS', stopbits='STOPBITS_ONE')
	mSerial2=MSerialPort(serialPort2,baudRate1)#, parity='PARITY_NONE', bytesize='EIGHTBITS', stopbits='STOPBITS_ONE')
	
	db_Name = "pruebaDB_USB.db"
	db_Table = "Variables_USB"
	db1 = Database(db_Name,db_Table)

	print('Conectado')
		
	t1 = threading.Thread(target = mSerial1.read_data)
	t1.start()
	t2 = threading.Thread(target = mSerial2.read_data)
	t2.start()
	time.sleep(2)

	print('---------------------------')
	for i in range(0,10):
		time.sleep(0.01)
		
		data1 = mSerial1.message
		print(f'Dato 1: {data1}')
		data1 = data1.replace("[","").replace("]","").replace("\r\n","")
		data1 = list(map(float, data1.split(",")))
		
		data2 = mSerial2.message
		print(f'Dato 2: {data2}')
		data2 = data2.replace("[","").replace("]","").replace("\r\n","")
		data2 = list(map(float, data2.split(",")))
		print(data1+data2)
		db1.save_data(data1+data2)
		print('---------------------------')

	mSerial1.read_flag = True
	mSerial1.port_close()
	mSerial2.read_flag = True
	mSerial2.port_close()
	print('Puertos cerrados!')
	t1.join()
	t2.join()
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
		self.port=serial.Serial(port,baud)
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
	def read_data(self):
		while True:
			data=self.port.readline()
			self.message=data.decode('ascii')
			if self.read_flag:
				self.read_flag = False
				break


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
