# Prueba multithreading usando Arduino UNO y Arduino Mega conectados por USB
# Se tiene un objeto que hereda de QThread para cada conexión y un objeto 
#  para la adquisición con un tiempo de muestreo determinado

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

		self.start_workers()

	def setupUi(self):
		uic.loadUi("prueba_pyqtgraph1.ui",self)
		self.button_start = self.findChild(QPushButton,"button_start")
		self.button_start.clicked.connect(self.start_aqcuisiton)
		self.button_stop = self.findChild(QPushButton,"button_stop")
		self.button_stop.clicked.connect(self.stop_aqcuisiton)
		self.button_pause = self.findChild(QPushButton,"button_pause")
		self.button_pause.clicked.connect(self.pause_resume_aqcuisiton)

		self.label_f_vx1 = self.findChild(QLabel,"label_fre_vx_1")
		self.label_f_vx2 = self.findChild(QLabel,"label_fre_vx_2")
		self.label_f_vx3 = self.findChild(QLabel,"label_fre_vx_3")
		self.label_f_vx4 = self.findChild(QLabel,"label_fre_vx_4")
		self.label_f_vx5 = self.findChild(QLabel,"label_fre_vx_5")
		self.label_f_vx6 = self.findChild(QLabel,"label_fre_vx_6")
		self.label_f_vx7 = self.findChild(QLabel,"label_fre_vx_7")

		self.plot_widget = self.findChild(PlotWidget,"plot_widget")
		self.plot_widget.setBackground('w')
		self.red_pen = mkPen(color=(255, 0, 0), width=2)

	def start_workers(self):
		serialPort1 = 'COM8' # Debe revisarse el puerto al que se conecta el GINS
		serialPort2 = 'COM9' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 9600
		
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

	def start_aqcuisiton(self):
		
		self.thread[3] = MAcquisiton(parent=None,index=3)
		self.thread[3].start()
		self.thread[3].data.connect(self.print_labels)
		self.thread[3].data.connect(self.plot_data)
		
		self.thread[1].data.connect(lambda: self.thread[3].update_val1(self.val1))
		self.thread[2].data.connect(lambda: self.thread[3].update_val2(self.val2))
		
		self.button_start.setEnabled(False)
		self.button_stop.setEnabled(True)
		#self.pushButton_3.setEnabled(False)
		
	def stop_aqcuisiton(self):
		self.thread[3].stop()
		self.button_start.setEnabled(True)
		self.button_stop.setEnabled(False)
	
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
		#self.label_f_vx1.setText(f'{self.val1}')
		# self.label_f_vx1.setText(f'{data["gyro_x"]}')
		# self.label_f_vx2.setText(f'{data["gyro_y"]}')
		# self.label_f_vx3.setText(f'{data["t_gins"]}')
		# self.label_f_vx4.setText(f'{data["fp"]}')
		# self.label_f_vx5.setText(f'{data["Td"]}')
		# self.label_f_vx6.setText(f'{data["t_cdaq"]}')

	def print_labels(self,val):
		print(f'Print labels: {val}')
		self.label_f_vx1.setText(f'{val[0]}')
		self.label_f_vx2.setText(f'{val[1]}')
		self.label_f_vx3.setText(f'{val[2]}')
		self.label_f_vx4.setText(f'{val[3]}')
		self.label_f_vx5.setText(f'{val[4]}')
		self.label_f_vx6.setText(f'{val[5]}')
		self.label_f_vx7.setText(f'{val[6]}')

	def plot_data(self,val):
		# plot data: x, y values
		if val[0]>0:
			self.line1.clear()
		if len(self.xdata)>=15:
			del self.xdata[0]
			del self.ydata[0]
		self.xdata.append(val[0])
		self.ydata.append(val[1])
		print(f'len_x = {len(self.xdata)}')
		#self.line1.clear()
		self.line1 = self.plot_widget.plot(self.xdata,self.ydata,pen=self.red_pen,symbol='+', symbolSize=20, symbolBrush=('b'))
		


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
	def send_data(self,data):
		number=self.port.write(data)
		return number
	def run(self):
		self.port_open()
		while True:
			time.sleep(0.001)
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
				print(e)
			self.data.emit(self.message)
	
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
			self.data.emit([t]+self.val1+self.val2)
			t += 1
	
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