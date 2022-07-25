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

	def setupUi(self):
		uic.loadUi("prueba_pyqtgraph1.ui",self)
		self.button_start = self.findChild(QPushButton,"button_start")
		self.button_start.clicked.connect(self.start_workers)
		self.button_stop = self.findChild(QPushButton,"button_stop")
		self.button_stop.clicked.connect(self.stop_workers)
		#self.button_pause = self.findChild(QPushButton,"button_pause")
		#self.button_pause.clicked.connect(self.pause_resume_aqcuisiton)
		self.label_f_vx1 = self.findChild(QLabel,"label_fre_vx_1")
		self.label_f_vx2 = self.findChild(QLabel,"label_fre_vx_2")
		self.label_f_vx3 = self.findChild(QLabel,"label_fre_vx_3")
		self.label_f_vx4 = self.findChild(QLabel,"label_fre_vx_4")
		self.label_f_vx5 = self.findChild(QLabel,"label_fre_vx_5")
		self.label_f_vx6 = self.findChild(QLabel,"label_fre_vx_6")
		self.label_f_vx7 = self.findChild(QLabel,"label_fre_vx_7")

	def start_worker_gins(self):
		serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 460800
		self.thread[1] = MSerialPort(serialPort,baudRate,parent=None,index=1)
		self.thread[1].start()
		self.thread[1].data.connect(self.print_data)
		#self.pushButton_3.setEnabled(False)
		
	def stop_worker_gins(self):
		self.thread[1].stop()
		#self.pushButton.setEnabled(True)

	def start_worker_cdaq(self):
		self.thread[2] = CDaq(parent=None,index=2)
		self.thread[2].start()
		self.thread[2].data.connect(self.print_data_2)
		#self.pushButton_3.setEnabled(False)
		
	def stop_worker_cdaq(self):
		self.thread[2].stop()
		#self.pushButton.setEnabled(True)

	
	def start_workers(self):
		serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 460800
		self.thread[1] = MSerialPort(serialPort,baudRate,parent=None,index=1)
		self.thread[1].start()
		self.thread[1].data.connect(self.print_data_gins)

		self.thread[2] = CDaq(parent=None,index=2)
		self.thread[2].start()
		self.thread[2].data.connect(self.print_data_cdaq)
		
	def stop_workers(self):
		self.thread[1].stop()
		self.thread[2].stop()
		#self.pushButton.setEnabled(True)

	def start_aqcuisiton(self):
		serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 460800
		self.thread[1] = DataAqcuisition(serialPort,baudRate,parent=None,index=1)
		self.thread[1].start()
		self.thread[1].data.connect(self.update_labels)
		self.button_start.setEnabled(False)
		self.button_stop.setEnabled(True)
		#self.pushButton_3.setEnabled(False)
		
	def stop_aqcuisiton(self):
		self.thread[1].stop()
		self.button_start.setEnabled(True)
		self.button_stop.setEnabled(False)
	
	def pause_resume_aqcuisiton(self):
		self.pause = not self.pause
		if self.pause:
			self.thread[1].pause()
			self.button_pause.setText("Resume")
		else:
			self.thread[1].resume()
			self.button_pause.setText("Pause")
		

	def print_data_gins(self,data):
		#print(f'data["gyro_x"]: {data["gyro_x"]}')
		self.label_f_vx1.setText(f'{data["gyro_x"]}')
		self.label_f_vx2.setText(f'{data["gyro_y"]}')
		self.label_f_vx3.setText(f'{data["t_gins"]}')

	def print_data_cdaq(self,data):
		#print(f'data["gyro_x"]: {data["gyro_x"]}')
		self.label_f_vx4.setText(f'{data["fp"]}')
		self.label_f_vx5.setText(f'{data["Td"]}')
		self.label_f_vx6.setText(f'{data["t_cdaq"]}')
	
	def update_labels(self,data):
		#print(f'data["gyro_x"]: {data["gyro_x"]}')
		self.label_f_vx1.setText(f'{data["gyro_x"]}')
		self.label_f_vx2.setText(f'{data["gyro_y"]}')
		self.label_f_vx3.setText(f'{data["t_gins"]}')
		self.label_f_vx4.setText(f'{data["fp"]}')
		self.label_f_vx5.setText(f'{data["Td"]}')
		self.label_f_vx6.setText(f'{data["t_cdaq"]}')


class MSerialPort(QThread):
	vals = dict()
	message = None
	read_flag = False
	data = pyqtSignal(dict)
	def __init__(self,port,baud,index=0,parent=None):
		super(MSerialPort, self).__init__(parent)
		self.index=index
		self.is_running = True
		self.port=serial.Serial(port,baud,bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1) #Para el GINS200
		self.port_open()
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
	def run(self):
		print("GINS iniciado en hilo ->",self.index)
		while True:
			#t1 = time.time()
			t1 = datetime.now()
			if not self.is_running:
				break
			out = ''
			while self.port.inWaiting() > 0: 
				out = self.port.read(self.port.inWaiting())#.decode('uint8')
			if out != '':
				self.message = self.get_gins_values(out.hex())
				t = datetime.now() - t1
				dt = t.total_seconds()
				self.message["t_gins"] = dt
				self.data.emit(self.message)
				
			#time.sleep(0.05)
	def stop(self):
		self.is_running = False
		print('GINS finalizado en hilo ->',self.index)
		self.port_close()
		self.terminate()
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


class CDaq(QThread):
	task1 = None
	task2 = None
	task3 = None
	data = pyqtSignal(dict)
	datos = {}
	read_flag = False
	devC = nidaqmx.system.device.Device('cDAQ9188')
	devC.reserve_network_device(True)
	min_V = -10
	max_V = 10
	def __init__(self,index=0,parent=None):
		super(CDaq, self).__init__(parent)
		self.index=index
		self.is_running = True
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
		
		#self.task1.timing.cfg_samp_clk_timing(rate=50000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		#self.task2.timing.cfg_samp_clk_timing(rate=50000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		#self.task3.timing.cfg_samp_clk_timing(rate=50000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		self.task1.timing.cfg_samp_clk_timing(rate=5000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2000)
		self.task2.timing.cfg_samp_clk_timing(rate=5000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2000)
		self.task3.timing.cfg_samp_clk_timing(rate=5000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2000)

	def task_close(self):
		self.task1.close()
		self.task2.close()
		self.task3.close()

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

	def run(self):
		print("Tarea cDAQ iniciada en hilo",self.index)
		while True:
			t1 = time.time()
			#time.sleep(0.038)
			if not self.is_running:
				break
			self.datos = self.list2dict(self.task1.read(number_of_samples_per_channel=1) + self.task2.read(number_of_samples_per_channel=1) + self.task3.read(number_of_samples_per_channel=1))
			#print(self.datos)
			self.datos["t_cdaq"] = time.time() - t1
			self.data.emit(self.datos)
			
			#print(f't_cdaq={t*1000}ms')
	def stop(self):
		self.is_running = False
		print("Tarea cDAQ terminada en hilo",self.index)
		self.task_close()
		self.terminate()

#---- Class aqcuisition
class DataAqcuisition(QThread):
	task1 = None
	task2 = None
	task3 = None

	vals = dict()
	message = None

	data = pyqtSignal(dict)
	datos = {}
	read_flag = False
	devC = nidaqmx.system.device.Device('cDAQ9188')
	devC.reserve_network_device(True)
	min_V = -10
	max_V = 10
	def __init__(self,port,baud,index=0,parent=None):
		super(DataAqcuisition, self).__init__(parent)
		self.index=index
		self.is_running = True
		self.is_paused = False
		
		self.port=serial.Serial(port,baud,bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1) #Para el GINS200
		self.port_open()
		
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
	
	def task_close(self):
		self.task1.close()
		self.task2.close()
		self.task3.close()
	
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
	
	def run(self):
		print("Tarea cDAQ iniciada en hilo ->",self.index)
		print("GINS iniciado en hilo ->",self.index)
		self.is_running = True
		d1 = {}
		d2 = {}
		while True:
			#time.sleep(0.002)
			t = time.time()
			if self.is_paused:
				continue
			if not self.is_running:
				break
			# Datos cDAQ
			d1 = self.list2dict(self.task1.read(number_of_samples_per_channel=1) + self.task2.read(number_of_samples_per_channel=1) + self.task3.read(number_of_samples_per_channel=1))
			# Datos GINS
			self.datos.update(d1)
			out = ''
			while self.port.inWaiting() > 0: 
				out = self.port.read(self.port.inWaiting())#.decode('uint8')
			if out != '':
				d2 = self.get_gins_values(out.hex())
			self.datos.update(d2)
			self.data.emit(self.datos)
			t -= time.time()
			print(f'{t*1000} ms')
			
	
	def pause(self):
		self.is_paused = True
		print("Tarea cDAQ pausada en hilo ->",self.index)
		print('GINS pausado en hilo ->',self.index)

	def resume(self):
		self.is_paused = False
		print("Tarea cDAQ continuada en hilo ->",self.index)
		print('GINS continuado en hilo ->',self.index)

	def stop(self):
		self.is_running = False
		print("Tarea cDAQ terminada en hilo ->",self.index)
		print('GINS finalizado en hilo ->',self.index)
		self.task_close()
		self.port_close()
		self.terminate()


if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	win = UI()
	win.show()
	sys.exit(app.exec())