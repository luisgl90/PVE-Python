import nidaqmx as daq
import nidaqmx
from nidaqmx import system
import time
#import matplotlib.pyplot as plt

#Fs = 2000;
#Ts = 1/Fs;
#reserve_network_device(True)

#print(system.Device.reserve_network_device())
#devList = system.System.devices
#print(f'Disp: {devList}')
devC = nidaqmx.system.device.Device('cDAQ9188')
devC.reserve_network_device(True)
print(devC)
print("Devs:---------------------------------------------")

devs1 = nidaqmx.system.system.System.devices

print(f"Devs: {nidaqmx.system.system.System.devices}")
print(f"Devs: {nidaqmx.system.device.Device.terminals}")
print(f"Devs ch: {nidaqmx.system.device.Device.compact_daq_chassis_device}")
#d1 = system.Device.add_network_device('169.254.77.229','cDAQ9188')
#print(f'Disp Eth: {d1}')
#d1.reserve_network_device()
#system.Device.reserve_network_device(devC)
#get_daq_device_inventory(1, number_of_devices=1)


with nidaqmx.Task() as task:
	#task.ai.channels.add_ai_voltage_chan("cDAQ1Mod1/ai0:1")
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai3")
	for i in range(0,61):
		#task.ai.channels.add_ai_voltage_chan("cDAQ9188Mod5/ai0:1")
		
		data = task.read(number_of_samples_per_channel=1)
		print(data)
		time.sleep(0.5)
		#plt.scatter(i,data[0],color='blue')
		#plt.pause(0.005)
		#plt.pause(Ts)
 
