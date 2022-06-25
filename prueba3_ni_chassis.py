# Pruebas de conexión con el chasis NI
# Pruebas de adquisición de datos de varios canales


#import nidaqmx as daq
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import time
import matplotlib.pyplot as plt


def main(args):

	#Fs = 2000;
	#Ts = 1/Fs;
	
	data = []

	with nidaqmx.Task() as task:
		task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai2")
		task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai2")
		
		#task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai2") # Rueda delantera 
		#task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai0") # 5ta rueda
		#task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai1") # Volante
		#task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod7/ai0") # Pedal
		#task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod8/ai0") # Acelerómetro X
		#task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod8/ai1") # Acelerómetro Y
		#task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod8/ai2") # Acelerómetro Z
		
		task.timing.cfg_samp_clk_timing(rate=1000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
	
		for i in range(0,10000):
		
			#data[0] = task1.read(number_of_samples_per_channel=1)
			#data[1] = task2.read(number_of_samples_per_channel=1)
			data = task.read()
			print(data)
			#print(task1.read(),task2.read())
			#plt.scatter(i,data[0],color='blue')
			#plt.pause(0.005)
			#plt.pause(Ts)
		
	task.close()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
