import time
import sqlite3
import threading
import pyqtgraph as pg
import serial
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QPushButton, QLabel
from PyQt5 import uic

class UI(QMainWindow):
	def __init__(self):
		super(UI,self).__init__()
		uic.loadUi("interfaz_app.ui",self)
		
		self.label_f_v = self.findChild(QLabel,"label_fre_v")
		self.label_f_ax = self.findChild(QLabel,"label_fre_ay")
		self.label_f_dh = self.findChild(QLabel,"label_fre_dh")
		self.label_e_v = self.findChild(QLabel,"label_est_v")
		self.label_e_ax = self.findChild(QLabel,"label_est_ay")
		self.label_e_dh = self.findChild(QLabel,"label_est_dh")
		self.label_e_dh = self.findChild(QLabel,"label_est_dh")

		self.widget_fre_plot.plot([],[])
		self.x_plot = []
		self.y_plot = []

		serialPort1 = 'COM8' # Debe revisarse el puerto al que se conecta el GINS
		serialPort2 = 'COM9' # Debe revisarse el puerto al que se conecta el GINS
		baudRate1 = 9600

		print('Inicio')
		self.mSerial1=MSerialPort(serialPort1,baudRate1)
		self.mSerial2=MSerialPort(serialPort2,baudRate1)
		
		db_Name = "pruebaDB_USB.db"
		db_Table = "Variables_USB"
		self.db1 = Database(db_Name,db_Table)

		print('Conectado')
			
		self.t1 = threading.Thread(target = self.mSerial1.read_data)
		self.t1.start()
		self.t2 = threading.Thread(target = self.mSerial2.read_data)
		self.t2.start()
		time.sleep(2)
		self.show()
		self.t3 = threading.Thread(target = self.acquisition_main)
		self.t3.start()


	def acquisition_main(self):
		print('---------------------------')
		print('-----Inicia adquisición-----')
		print('---------------------------')
		for i in range(0,50):
			time.sleep(0.1)
			
			data1 = self.mSerial1.message
			print(f'Dato 1: {data1}')
			data1 = data1.replace("[","").replace("]","").replace("\r\n","")
			data1 = list(map(float, data1.split(",")))
			
			data2 = self.mSerial2.message
			print(f'Dato 2: {data2}')
			data2 = data2.replace("[","").replace("]","").replace("\r\n","")
			data2 = list(map(float, data2.split(",")))
			
			data = data1+data2
			#self.plot(i*0.01,round(data[0],4))
			self.x_plot.append(i*0.01)
			self.y_plot.append(round(data[0],4))
			self.widget_fre_plot.plot(self.x_plot,self.y_plot)
			print(data)

			self.label_f_v.setText(str(round(i+data[0],4)))
			self.label_f_ax.setText(str(round(i+data[1],4)))
			self.label_f_dh.setText(str(round(i+data[2],4)))

			#db1.save_data(data1+data2)
			print('---------------------------')

		self.mSerial1.read_flag = True
		time.sleep(0.1)
		self.mSerial1.port_close()
		self.mSerial2.read_flag = True
		time.sleep(0.1)
		self.mSerial2.port_close()
		print('Puertos cerrados!')
		time.sleep(0.1)
		self.t1.join()
		self.t2.join()
		print('Hilos finalizados!')

	def plot(self,new_x,new_y):
		self.x_plot.append(new_x)
		self.y_plot.append(new_y)
		self.widget_fre_plot.plot(self.x_plot,self.y_plot)

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
	app = QApplication(sys.argv)
	UIWindow = UI()
	app.exec_()
	#sys.exit(main(sys.argv))