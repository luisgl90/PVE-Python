# Pruebas de conexión con el chasis NI
# Pruebas de adquisición de datos de varios canales - Chasís NI
# Comunicación serial - GINS200

#import nidaqmx as daq
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import time
import matplotlib.pyplot as plt
import serial
import threading

def main(args):

	#Fs = 2000;
	#Ts = 1/Fs;
	
	data = []
	
	serialPort = 'COM7' # Debe revisarse el puerto al que se conecta el GINS
	#baudRate = 9600
	baudRate = 460800
	
	## GINS200=serial('COM5','BaudRate',460800,'Parity','none','DataBits',8,'StopBits',1,'Terminator','CR')
	mSerial=MSerialPort(serialPort,baudRate)#, parity='PARITY_NONE', bytesize='EIGHTBITS', stopbits='STOPBITS_ONE')
	#thread.start_new_thread(mSerial.read_data,())
	t1 = threading.Thread(target = mSerial.read_data)
	t1.start()
	
	# with nidaqmx.Task() as task:
		# task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai2")
		# task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai2")
		
		
		
		# task.timing.cfg_samp_clk_timing(rate=1000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
	
		# for i in range(0,10000):
		
			# #data[0] = task1.read(number_of_samples_per_channel=1)
			# #data[1] = task2.read(number_of_samples_per_channel=1)
			# dataNI = task.read()
			# print(data)
			# #print(task1.read(),task2.read())
			# #plt.scatter(i,data[0],color='blue')
			# #plt.pause(0.005)
			# #plt.pause(Ts)
	# task.close()
	
	print('---------------------------')
	for i in range(0,10):
		time.sleep(0.1)
		print(f'Dato: {mSerial.message}')
		print(mSerial.message)
		print('---------------------------')
	mSerial.port_close()
	

class MSerialPort:
	message=''
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
			self.message=data

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
