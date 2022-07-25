from time import sleep
import serial
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
	QApplication,
	QLabel,
	QMainWindow,
	QPushButton,
	QVBoxLayout,
	QWidget,
)
from PyQt5 import uic

class MSerialPort(QObject):
	finished = pyqtSignal()
	data = pyqtSignal(list)
	def __init__(self,port,baud,parent=None):
		super(MSerialPort,self).__init__(parent)
		self.is_running = False
		self.is_paused = False
		self.port=serial.Serial(port,baud)
		self.port_open()
	def port_open(self):
		if not self.port.isOpen():
			self.port.open()"
	def port_close(self):
		self.port.close()
	def send_data(self,data):
		number=self.port.write(data)
		return number
	def run(self):
		self.port_open()
		while True:
			#sleep(0.1)
			if self.is_paused:
				continue
			if self.is_running:
				break
			try:
				data1 = self.port.readline().decode('ascii')
				data1 = data1.replace("[","").replace("]","").replace("\r\n","")
				data1 = list(map(float, data1.split(",")))
				print(data1)
				self.data.emit(data1)
			except Exception as e:
				print(e)
				self.data.emit([])
	
	def pause(self):
		self.is_paused = True
		print(f'Tarea {self.name} pausada en hilo')

	def resume(self):
		self.is_paused = False
		print(f'Tarea {self.name} continuada en hilo')

	def stop(self):
		self.is_running = False
		print(f'Tarea {self.name} terminada en hilo')
		self.finished.emit()
		self.port_close()
		self.terminate()

# Step 1: Create a worker class
class Worker(QObject):
	finished = pyqtSignal()
	progress = pyqtSignal(float)
	def run(self):
		"""Long-running task."""
		for i in range(20):
			sleep(0.7)
			self.progress.emit(float(1.1**i))
		self.finished.emit()


class PlotWorker(QObject):
	plot_signal = pyqtSignal()
	def run(self):
		"""Long-running task."""
		#sleep(3)
		for i in range(30):
			sleep(0.1)
			self.plot_signal.emit()
		#self.finished.emit()


class Window(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.val1 = 0
		self.clicksCount = 0
		self.finish = pyqtSignal()
		self.setupUi()
		
	def setupUi(self):
		uic.loadUi("prueba_pyqtgraph1.ui",self)
		self.button_start = self.findChild(QPushButton,"button_start")
		self.button_start.clicked.connect(self.runLongTask)
		self.button_stop = self.findChild(QPushButton,"button_stop")
		#self.button_stop.clicked.connect(lambda: self.finish.emit)
		self.button_pause = self.findChild(QPushButton,"button_pause")
		#self.button_stop.clicked.connect(self.thread.quit)
		self.label_f_vx1 = self.findChild(QLabel,"label_fre_vx_1")
		self.label_f_vx2 = self.findChild(QLabel,"label_fre_vx_2")
		self.label_f_vx3 = self.findChild(QLabel,"label_fre_vx_3")
		self.label_f_vx4 = self.findChild(QLabel,"label_fre_vx_4")
		self.label_f_vx5 = self.findChild(QLabel,"label_fre_vx_5")
		self.label_f_vx6 = self.findChild(QLabel,"label_fre_vx_6")
		self.label_f_vx7 = self.findChild(QLabel,"label_fre_vx_7")

	def countClicks(self):
		self.clicksCount += 1
		self.clicksLabel.setText(f"Counting: {self.clicksCount} clicks")

	def reportProgress(self, n):
		self.stepLabel.setText(f"Long-Running Step: {n}")

	def reportWProgress(self, n):
		print(f'Val 1 update: {self.val1}')
	
	def reportData(self, v):
		self.val1 = v
		#self.label_f_vx1.setText(f"{self.val1}")
		print(f'Val 1 update: {self.val1}')

	def update_gui(self, v):
		self.label_f_vx1.setText(f"{v[0]}")
		#print(f'Val 1 update: {self.val1}')

	def print_val(self,val):
		print(f'Print val = {val}')

	def runLongTask(self):
		# Step 2: Create a QThread object
		self.thread = QThread()
		# Step 3: Create a worker object
		#self.worker = Worker()
		serialPort = 'COM8' # Debe revisarse el puerto al que se conecta el GINS
		baudRate = 9600
		self.ser = MSerialPort(serialPort,baudRate)
		self.worker = PlotWorker()

		# Step 4: Move worker to the thread
		self.ser.moveToThread(self.thread)
		self.worker.moveToThread(self.thread)
		# Step 5: Connect signals and slots
		self.thread.started.connect(self.ser.run)
		self.thread.started.connect(self.worker.run)

		self.ser.finished.connect(self.thread.quit)
		self.ser.finished.connect(self.ser.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		self.ser.data.connect(self.reportData)
		#self.ser.data.connect(lambda: self.print_val(self.val1))

		self.worker.plot_signal.connect(lambda: self.update_gui(self.val1))
		#self.worker.progress.connect(self.reportWProgress)
		#self.button_stop.connect(self.ser.stop)
		#self.button_pause.connect(self.ser.stop)
		#self.finish.connect(self.ser.stop)
		# Step 6: Start the thread
		self.thread.start()

		# Final resets
		self.button_start.setEnabled(False)
		self.thread.finished.connect(
			lambda: self.button_stop.setEnabled(True)
		)
		self.thread.finished.connect(
			lambda: self.label_f_vx1.setText("0")
		)

	def stop_task(self):
		self.ser.stop()

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	win = Window()
	win.show()
	sys.exit(app.exec())