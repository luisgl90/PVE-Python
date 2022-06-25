# Pruebas de conexión con el chasis NI
# Pruebas de adquisición de datos de varios canales - Chasís NI
# Comunicación serial - GINS200

#import nidaqmx as daq
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import time
import matplotlib.pyplot as plt
import serial
from bitstring import BitArray
import struct

def main(args):

	serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
	baudRate = 460800
	#baudRate = 230400 # Default
	
	## GINS200=serial('COM5','BaudRate',460800,'Parity','none','DataBits',8,'StopBits',1,'Terminator','CR')
	#mSerial=MSerialPort(serialPort,baudRate)#, parity='PARITY_NONE', bytesize='EIGHTBITS', stopbits='STOPBITS_ONE')
	print('\n-------------Start--------------')
	s = serial.Serial(serialPort,baudRate,bytesize=serial.EIGHTBITS, 
		parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
	if not s.isOpen():
		s.open()
		print(f"Puerto {serialPort} abierto")
	for i in range(51):
		time.sleep(0.2)
		print(f"---Data {i}---")
		out = ''
		while s.inWaiting() > 0: 
			out = s.read(s.inWaiting())#.decode('uint8')
		if out != '':
			print(out)
			data = out.hex()
			#start_data = data.find('aa550364')
			#print(data[start_data:start_data+200])
			#get_gins_values(data[start_data:start_data+200])
			get_gins_values(data)
		#res = s.read().decode('ascii')
		#print(res)
	#s.close()
	
	
	
	
	print('\n-------------Finished--------------')
	# for i in range(0,10):
		# time.sleep(0.1)
		# print('Dato:')
		# print(mSerial.message)
		# print('---------------------------')
	# mSerial.port_close()
	
def get_gins_values(data):
	#data = str(hex(int(BitArray(in_stream).bin,2)))
	try:
		start_data = data.find('aa550364')
		out_stream = data[start_data:start_data+200]
		print(out_stream)
		
		# Get values from separated bytes
		sens_gyro = 1e-4
		sens_acc = 1e-5
		sens_magn = 1e-2
		sens_hbar = 1e-2
		
		gyro_x = sens_gyro*float(hex2sint(out_stream[8:14],3))
		gyro_y = sens_gyro*float(hex2sint(out_stream[14:20],3))
		gyro_z = sens_gyro*float(hex2sint(out_stream[20:26],3))
		print(f'[gyro_x,gyro_y,gyro_z]: [{gyro_x},{gyro_y},{gyro_z}]')
		acc_x = sens_acc*float(hex2sint(out_stream[26:32],3))
		acc_y = sens_acc*float(hex2sint(out_stream[32:38],3))
		acc_z = sens_acc*float(hex2sint(out_stream[38:44],3))
		print(f'[acc_x,acc_y,acc_z]: [{acc_x},{acc_y},{acc_z}]')
		magn_x = sens_magn*float(hex2sint(out_stream[44:48],2))
		magn_y = sens_magn*float(hex2sint(out_stream[48:52],2))
		magn_z = sens_magn*float(hex2sint(out_stream[52:56],2))
		print(f'[magn_x,magn_y,magn_z]: [{magn_x},{magn_y},{magn_z}]')
		h_bar = sens_hbar*float(hex2sint(out_stream[56:62],3))
		#acc_y = sens_acc*float(hex2sint(out_stream[32:38],3))
		print(f'[h_bar]: [{h_bar}]')
	except:
		print('---Dato incompleto---')
		
	
def hex2sint(val,num_bytes):
	sign = False
	if num_bytes==3:
		bin_data = "{0:024b}".format(int(val, 16))
	elif num_bytes==2:
		bin_data = "{0:016b}".format(int(val, 16))
	return BitArray(bin=bin_data).int
	

class MSerialPort:
	message=''
	def __init__(self,port,baud):
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
	def read_data(self):
		while True:
			data=self.port.read().decode('utf-8')
			self.message+=data

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
