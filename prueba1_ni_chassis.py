#import nidaqmx as daq
import nidaqmx
import time
import matplotlib.pyplot as plt

Fs = 2000;
Ts = 1/Fs;

with nidaqmx.Task() as task:
	#task.ai.channels.add_ai_voltage_chan("cDAQ1Mod1/ai0:1")
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai3")
	for i in range(0,61):
		#task.ai.channels.add_ai_voltage_chan("cDAQ9188Mod5/ai0:1")
		
		data = task.read(number_of_samples_per_channel=1)
		#print(data)
		plt.scatter(i,data[0],color='blue')
		plt.pause(0.005)
		#plt.pause(Ts)
 
