# Código para guardar un diccionario con n muestras en n filas de una base de datos determinada
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

	def dict2tup(self,data):
		create_table_str = self.create_table_str
		dict_keys = list(data.keys())
		dict_values = list(data.values())
		for indx in dict_keys:
			create_table_str += indx + " REAL NOT NULL, "
		create_table_str += "PRIMARY KEY (" + dict_keys[0] + "))" 

		return tuple(dict_keys),tuple(dict_values),create_table_str
	
	def dict2tuplist(self,data):
		create_table_str = self.create_table_str
		dict_keys = list(data.keys())
		dict_values = list(data.values())
		for indx in dict_keys:
			create_table_str += indx + " REAL NOT NULL, "
		create_table_str += "PRIMARY KEY (" + dict_keys[0] + "))" 
		#print(f'k_data = {dict_keys}')
		tup_list = []
		for i in range(len(dict_values[0])):
			tup = []
			for k in dict_values:
				tup.append(k[i])
			tup_list.append(tuple(tup))
		return tuple(dict_keys),tup_list,create_table_str

	def insert2db(self,data):
		if isinstance(list(data.values())[0],list):
			tup_keys,list_values,create_table_str = self.dict2tuplist(data)
			#tup_keys,tup_values,create_table_str = self.dict2tup(data)
			#print(f'tup_values = {tup_values}')
			print(f'tup_keys = {tup_keys}')
			print(f'list_values = {list_values}')
			try:
				#cursor.execute("CREATE TABLE IF NOT EXISTS " + db_Table + " (t REAL NOT NULL, Dist REAL NOT NULL, Fp REAL NOT NULL, Vx REAL NOT NULL, Vy REAL NOT NULL, Vz REAL NOT NULL, Ax REAL NOT NULL, Ay REAL NOT NULL, Az REAL NOT NULL, Ti REAL NOT NULL, Td REAL NOT NULL, PRIMARY KEY (t))")
				self.cursor.execute(create_table_str)
				#cursor.execute("INSERT INTO " + db_Table + "(t, Dist, Fp, Vx, Vy, Vz, Ax, Ay, Az, Ti, Td) VALUES(?,?,?,?,?,?,?,?,?,?,?)",tuple(data))
				#self.cursor.execute(f"\n\nINSERT INTO {self.db_table} {tuple(list_indexes)} VALUES {str(tuple(list_values))}")
				#values = ', '.join(map(str, list_values))
				sql = "INSERT INTO " + self.db_table + " " + str(tup_keys) + " VALUES ("
				for i in range(len(tup_keys)):
					if i==0:
						sql += "?"
					else:
						sql += ",?"
				sql += ")"
				print(f'sql = {sql}')
				#self.cursor.execute(f"\n\nINSERT INTO {self.db_table} {tup_keys} VALUES {str(tup_values)}")
				self.cursor.executemany(sql,list_values)
				self.db_conn.commit()
			except Exception as ex:
				print(ex)
		else:
			tup_keys,tup_values,create_table_str = self.dict2tup(data)
			#print(f'tup_values = {tup_values}')
			try:
				#cursor.execute("CREATE TABLE IF NOT EXISTS " + db_Table + " (t REAL NOT NULL, Dist REAL NOT NULL, Fp REAL NOT NULL, Vx REAL NOT NULL, Vy REAL NOT NULL, Vz REAL NOT NULL, Ax REAL NOT NULL, Ay REAL NOT NULL, Az REAL NOT NULL, Ti REAL NOT NULL, Td REAL NOT NULL, PRIMARY KEY (t))")
				self.cursor.execute(create_table_str)
				#cursor.execute("INSERT INTO " + db_Table + "(t, Dist, Fp, Vx, Vy, Vz, Ax, Ay, Az, Ti, Td) VALUES(?,?,?,?,?,?,?,?,?,?,?)",tuple(data))
				#self.cursor.execute(f"\n\nINSERT INTO {self.db_table} {tuple(list_indexes)} VALUES {str(tuple(list_values))}")
				self.cursor.execute(f"\n\nINSERT INTO {self.db_table} {tup_keys} VALUES {str(tup_values)}")
				self.db_conn.commit()
			except Exception as ex:
				print(ex)


db_Name = "pruebaDB_cDAQ2.db"
db_Table = "Variables_cDAQ2"

data_cdaq = {}
data_cdaq["t"] = [0.0,0.1,0.2,0.3,0.4,0.5]
data_cdaq["fp"] = [1.0,1.1,1.2,1.3,1.4,1.5,1.6]
data_cdaq["Td"] = [0.0,0.1,0.2,0.3,0.4,0.5]
data_cdaq["Ti"] = [1.0,1.1,1.2,1.3,1.4,1.5,1.6]
data_cdaq["Rdel"] = [0.0,0.1,0.2,0.3,0.4,0.5]
data_cdaq["R5a"] = [1.0,1.1,1.2,1.3,1.4,1.5,1.6]
data_cdaq["Rder"] = [0.0,0.1,0.2,0.3,0.4,0.5]
data_cdaq["Rizq"] = [1.0,1.1,1.2,1.3,1.4,1.5,1.6]
data_cdaq["Vol"] = [0.0,0.1,0.2,0.3,0.4,0.5]
data_cdaq["AccX"] = [1.0,1.1,1.2,1.3,1.4,1.5,1.6]
data_cdaq["AccY"] = [0.0,0.1,0.2,0.3,0.4,0.5]
data_cdaq["AccZ"] = [1.0,1.1,1.2,1.3,1.4,1.5,1.6]

# data_cdaq["t"] = 0.0
# data_cdaq["fp"] = 0.1
# data_cdaq["Td"] = 0.2
# data_cdaq["Ti"] = 0.3
# data_cdaq["Rdel"] = 0.4
# data_cdaq["R5a"] = 0.5
# data_cdaq["Rder"] = 0.6
# data_cdaq["Rizq"] = 0.7
# data_cdaq["Vol"] = 0.8
# data_cdaq["AccX"] = 0.9
# data_cdaq["AccY"] = 1.0
# data_cdaq["AccZ"] = 1.1

print(type(list(data_cdaq.values())[0]))

d2db = Dict2Db(db_Table,db_Name)
d2db.insert2db(data_cdaq)
data_cdaq["t"] = [x+0.6 for x in data_cdaq["t"]]
d2db.insert2db(data_cdaq)
data_cdaq["t"] = [x+0.6 for x in data_cdaq["t"]]
d2db.insert2db(data_cdaq)

# d = [(1,2),(1,3)]
# print(len(d[0]))

# for i in range(100):
# 	d2db.insert2db(data_cdaq)
# 	print(f'Dato insertado: {data_cdaq}')
# 	for ind in data_cdaq:
# 		data_cdaq[ind] += 0.1

# k_data = list(data_cdaq.keys())
# print(f'k_data = {k_data}')
# aa = []
# for i in range(len(data_cdaq[k_data[0]])):
# 	a = []
# 	for k in k_data:
# 		a.append(data_cdaq[k][i])
# 	aa.append(tuple(a))

# print(aa)

#print(len(data_cdaq["dato"]))
