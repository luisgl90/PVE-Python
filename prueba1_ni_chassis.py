#Código para la prueba de los sensores conectados al chasís NI cDAQ-9188

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
device_name = 'cDAQ9188'
devC = nidaqmx.system.device.Device(device_name)
devC.reserve_network_device(True)
print(devC)
#print(f'Meas types: {devC.ai_meas_types}')
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

#devC = nidaqmx.system.device.Device('cDAQ9188')
#devC.reserve_network_device(True)

min_V = -10
max_V = 10

while True:
	print("Escoja una prueba:\n\t1. Acelerómetros\n\t2. Temperatura en frenos\n\t3. Rueda delantera\n\t4. Ruedas y volante\n\t5. Pedal de freno\n\t6. Pedal y temperaturas\n\t0. Todos los sensores")
	opt = int(input())

	with nidaqmx.Task() as task1, nidaqmx.Task() as task2, nidaqmx.Task() as task3:
		
		if opt in (0,5,6):
			#Config módulo 7
			c7_0 = task1.ai_channels.add_ai_bridge_chan("cDAQ9188Mod7/ai0",name_to_assign_to_channel='c7_0',
				bridge_config=nidaqmx.constants.BridgeConfiguration.FULL_BRIDGE,
				nominal_bridge_resistance=700.0)	#Pedal
			#print(c7_0)
			#print(c7_0.ai_meas_type)
		if opt in (0,2,6):
			#Config módulo 2
			c2_0 = task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai0",name_to_assign_to_channel='c2_0',
				min_val=min_V,max_val=max_V)	#Temp der
			#print(c2_0)
			#c2_0.ai_meas_type = nidaqmx.constants.UsageTypeAI.VOLTAGE
			c2_1 = task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai1",name_to_assign_to_channel='c2_1',
				min_val=min_V,max_val=max_V)	#Temp izq
			#print(c2_1)
			#c2_1.ai_meas_type = nidaqmx.constants.UsageTypeAI.VOLTAGE
		if opt in (0,3):
			task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai6",min_val=min_V,max_val=max_V)	#Rueda delantera
		if opt in (0,4):
			#Config módulo 3
			task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai0",min_val=min_V,max_val=max_V)	#5ta rueda
			task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai1",min_val=min_V,max_val=max_V)	#Rueda izq
			task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai2",min_val=min_V,max_val=max_V)	#Rueda der
			task2.ai_channels.add_ai_voltage_chan("cDAQ9188Mod3/ai3",min_val=min_V,max_val=max_V)	#Volante
		if opt in (0,1):
			#Config módulo 8
			#sensX=99.07e-3	#mV/g	10.10e-3; %V/ms-2  
			#sensY=97.08e-3	#mV/g	9.89e-3; %V/ms-2   
			#sensZ=101.7e-3	#mV/g	10.38e-3; %V/ms-2 
			sensX=10.10e-3	#V/ms-2  
			sensY=9.89e-3	#V/ms-2   
			sensZ=10.38e-3	#V/ms-2 
			task3.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai0",
				units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
				sensitivity=sensX, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc x
			task3.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai1",
				units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
				sensitivity=sensY, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc y
			task3.ai_channels.add_ai_accel_chan("cDAQ9188Mod8/ai2",
				units=nidaqmx.constants.AccelUnits.METERS_PER_SECOND_SQUARED, 
				sensitivity=sensZ, sensitivity_units=nidaqmx.constants.AccelSensitivityUnits.VOLTS_PER_G)	#Acc z
		#else:
		#	print("Escoja una prueba válida")
		#	continue
		
		#print(f'Meas types: {devC.ai_meas_types}')
		#print(f'Physical channels: {devC.ai_physical_chans}')
		#print(nidaqmx.system._collections.physical_channel_collection.PhysicalChannelCollection(device_name).all)
		spc = 200
		# task1.timing.cfg_samp_clk_timing(rate=3000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=spc)
		# task2.timing.cfg_samp_clk_timing(rate=3000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=spc)
		# task3.timing.cfg_samp_clk_timing(rate=3000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=spc)
		task1.timing.cfg_samp_clk_timing(rate=12000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		task2.timing.cfg_samp_clk_timing(rate=12000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		task3.timing.cfg_samp_clk_timing(rate=12000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		
		#print(f'c7_0.ai_meas_type = {c7_0.ai_meas_type}')
		#print(f'c2_0.ai_meas_type = {c2_0.ai_meas_type}')
		#print(f'c2_1.ai_meas_type = {c2_1.ai_meas_type}')

		t = []
		res = []
		data = []

		t_ant = 0
		v_cicle = False
		v_ant = 0

		for i in range(0,3000):
			#task.ai.channels.add_ai_voltage_chan("cDAQ9188Mod5/ai0:1")
			start_time = time.time()
			#print(task.in_stream.channels_to_read)
			#if opt==3:
			#data = task2.read(number_of_samples_per_channel=1)
			#else:
			data = task1.read(number_of_samples_per_channel=1) + task2.read(number_of_samples_per_channel=1) + task3.read(number_of_samples_per_channel=1)
			
			# res = []
			# for d in data:
			# 	if isinstance(d,list):
			# 		res.append(float(d[0]))
			# 	else:
			# 		res.append(float(d))
			# print(f'res: {res[0]}')
			
			# #if opt==3:
			# if v_ant<2 and res[0]>=4.0:
			# 	print('flanco')
			# 	tn=time.time()
			# 	t_ant=tn-t_ant
			# 	v_ant = res[0]
			# 	vel = (4/tn)*(0.3/360)
			# else:
			# 	vel = 0
			# print(f'vel={vel}')


			#for d in data:
			#	if isinstance(d, list):
			#		res.append(d[0])
			#	else:
			#		res.append(d)
			
			# if opt==1:
			# 	print(data)
			# elif opt==2:
			# 	sens_T=12.5e-3; #mV/oC
			# 	print(f' {type(data)}: {data}')
			# 	print([(temp[0])/sens_T for temp in data])
			# 	print(data)
			# elif opt==4:
			# 	print(data)
			# elif opt==5:
			# 	pedal_offset = 1.59e-5
			# 	Vpedal=(data[0]-pedal_offset)*1e3; #mV
			# 	Mpedal=57.57*Vpedal; #Mass of the pedal
			# 	Fpedal=Mpedal*9.8; #kgm/s2 / N
			# 	print(f'{data[0]} -> {Fpedal}')
			#time.sleep(0.01)
			#plt.scatter(i,data[0],color='blue')
			#plt.pause(0.005)
			#plt.pause(Ts)
			#time.sleep(0.00005)
			t.append((time.time() - start_time)*1000)
			print(f'--- {t[i]} ms ---')
			#print('[fp,Td,Ti,Rdel,5aR,Rder,Rizq,Vol,AccX,AccY,AccZ]')
			#print(f'{data}\n')
			#print(f'{res}\n')
		
		print(f'tprom = {(sum(t)/len(t))} ms')


