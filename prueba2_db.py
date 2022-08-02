# Código para guardar un diccionario en una fila de una base de datos determinada
# Clase para guardar los datos de un diccionario en una BD

import sqlite3

class Dict2Db():
	list_indexes = []
	list_values = []
	create_table_str = ''
	db_conn = None
	def __init__(self,db_table,db_name):
		super(Dict2Db, self).__init__()
		self.db_table = db_table
		self.db_name = db_name
		self.db_conn = sqlite3.connect("database/" + self.db_name)
		self.cursor = self.db_conn.cursor()
		self.create_table_str = "CREATE TABLE IF NOT EXISTS " + self.db_table + " ("

	def __conv_dict(self,data):
		list_indexes = []
		list_values = []
		create_table_str = self.create_table_str
		for indx,val in data.items():
			create_table_str += indx + " REAL NOT NULL, "
			list_indexes.append(indx)
			list_values.append(val)
		create_table_str += "PRIMARY KEY (" + list_indexes[0] + "))" 

		return list_indexes,list_values,create_table_str

		#print(create_table_str)
		#print(f"\n\nINSERT INTO {db_Table} {(tuple(list_indexes))} VALUES {str(tuple(list_values))}")
	
	def insert2db(self,data):
		list_indexes,list_values,create_table_str = self.__conv_dict(data)
		try:
			#cursor.execute("CREATE TABLE IF NOT EXISTS " + db_Table + " (t REAL NOT NULL, Dist REAL NOT NULL, Fp REAL NOT NULL, Vx REAL NOT NULL, Vy REAL NOT NULL, Vz REAL NOT NULL, Ax REAL NOT NULL, Ay REAL NOT NULL, Az REAL NOT NULL, Ti REAL NOT NULL, Td REAL NOT NULL, PRIMARY KEY (t))")
			self.cursor.execute(create_table_str)
			#cursor.execute("INSERT INTO " + db_Table + "(t, Dist, Fp, Vx, Vy, Vz, Ax, Ay, Az, Ti, Td) VALUES(?,?,?,?,?,?,?,?,?,?,?)",tuple(data))
			self.cursor.execute(f"\n\nINSERT INTO {self.db_table} {(tuple(list_indexes))} VALUES {str(tuple(list_values))}")
			self.db_conn.commit()
		except Exception as ex:
			print(ex)


db_Name = "pruebaDB_cDAQ1.db"
db_Table = "Variables_cDAQ1"

data_cdaq = {}
data_cdaq["t"] = 0.0
data_cdaq["fp"] = 1.0
data_cdaq["Td"] = 1.1
data_cdaq["Ti"] = 1.2
data_cdaq["Rdel"] = 1.3
data_cdaq["R5a"] = 1.4
data_cdaq["Rder"] = 1.5
data_cdaq["Rizq"] = 1.6
data_cdaq["Vol"] = 1.7
data_cdaq["AccX"] = 1.8
data_cdaq["AccY"] = 1.9
data_cdaq["AccZ"] = 2.0


d2db = Dict2Db(db_Table,db_Name)

for i in range(100):
	d2db.insert2db(data_cdaq)
	print(f'Dato insertado: {data_cdaq}')
	for ind in data_cdaq:
		data_cdaq[ind] += 0.1