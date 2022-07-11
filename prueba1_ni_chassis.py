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

#devs1 = nidaqmx.system.system.System.devices

#print(f"Devs: {nidaqmx.system.system.System.devices}")
#print(f"Devs: {nidaqmx.system.device.Device.terminals}")
#print(f"Devs ch: {nidaqmx.system.device.Device.compact_daq_chassis_device}")
#d1 = system.Device.add_network_device('169.254.77.229','cDAQ9188')
#print(f'Disp Eth: {d1}')
#d1.reserve_network_device()
#system.Device.reserve_network_device(devC)
#get_daq_device_inventory(1, number_of_devices=1)


with nidaqmx.Task() as task:
	#task.ai.channels.add_ai_voltage_chan("cDAQ1Mod1/ai0:1")
	
	#Config módulo 2
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai0")	#Temp der
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai1")	#Temp izq
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai2")	#Rueda delantera
	#Config módulo 3
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai0")	#5ta rueda
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai1")	#Rueda izq
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai2")	#Rueda der
	task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai3")	#Volante
	#Config módulo 7
	task.ai_channels.add_ai_bridge_chan("cDAQ9188Mod7/ai0",
		bridge_config=nidaqmx.constants.BridgeConfiguration.FULL_BRIDGE,
		nominal_bridge_resistance=700.0)	#Pedal
	#Config módulo 8
	sensX=99.07e-3	#V/g	10.10e-3; %V/ms-2  
	sensY=97.08e-3	#V/g	9.89e-3; %V/ms-2   
	sensZ=101.7e-3	#V/g	10.38e-3; %V/ms-2 
	task.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai0",
		units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
		sensitivity=sensX, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc x
	task.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai1",
		units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
		sensitivity=sensY, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc y
	task.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai2",
		units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
		sensitivity=sensZ, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc z

	task.timing.cfg_samp_clk_timing(rate=100,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
	
	for i in range(0,61):
		#task.ai.channels.add_ai_voltage_chan("cDAQ9188Mod5/ai0:1")
		
		data = task.read(number_of_samples_per_channel=11)
		print(data)
		time.sleep(0.5)
		#plt.scatter(i,data[0],color='blue')
		#plt.pause(0.005)
		#plt.pause(Ts)
 
