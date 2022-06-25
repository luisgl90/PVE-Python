# -*- coding: utf-8 -*-

import nidaqmx
import sqlite3

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import serial

app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('Live plot from NI')
curve = p.plot()

data = [0]
#raw=serial.Serial("/dev/ttyACM0",9600)
#raw.open()

task = nidaqmx.Task()
task.ai_channels.add_ai_voltage_chan("cDAQ9188Mod2/ai3")

db_Name = "pruebaDB2.db"
db_Table = "Variables_PEV"
db_conn = None
cursor = None

db_conn = sqlite3.connect("database/" + db_Name)
cursor = db_conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS " + db_Table + " (n INT, V FLOAT, PRIMARY KEY (n))")


def update():
	global curve, data
	line = task.read(number_of_samples_per_channel=1)
	#line = raw.readline()
	print('Value:',line[0])
	print("Type:",type(line[0]))
	data.append(line[0])
	#xdata = np.array(data, dtype='float64')
	xdata = np.array(data)
	curve.setData(xdata)
	app.processEvents()
	
	try:
		cursor.execute("INSERT INTO " + db_Table + "(V) VALUES(?)",tuple([line[0]]))
		db_conn.commit()
	except Exception as ex:
		print('Error:',ex)
    

timer = QtCore.QTimer()
timer.timeout.connect(update)
#timer.setInterval(5)
timer.start(0)


if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
