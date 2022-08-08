import sqlite3

data = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9,10.10]
data2 = [0.1,2.1,3.2,4.3,5.4,6.5,7.6,8.7,9.8,10.9,11.10]

db_Name = "pruebaDB1.db"
db_Table = "Variables_PEV"
db_conn = None

try:
	db_conn = sqlite3.connect("database/" + db_Name)
	cursor = db_conn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS " + db_Table + " (t REAL AUTO_INCREMENT, Dist REAL NOT NULL, Fp REAL NOT NULL, Vx REAL NOT NULL, Vy REAL NOT NULL, Vz REAL NOT NULL, Ax REAL NOT NULL, Ay REAL NOT NULL, Az REAL NOT NULL, Ti REAL NOT NULL, Td REAL NOT NULL, PRIMARY KEY (t))")
	
	cursor.execute("INSERT INTO " + db_Table + "(Dist, Fp, Vx, Vy, Vz, Ax, Ay, Az, Ti, Td) VALUES(?,?,?,?,?,?,?,?,?,?)",tuple(data[1:]))
	db_conn.commit()
	
	cursor.execute("INSERT INTO " + db_Table + "(Dist, Fp, Vx, Vy, Vz, Ax, Ay, Az, Ti, Td) VALUES(?,?,?,?,?,?,?,?,?,?)",tuple(data2[1:]))
	db_conn.commit()
	
except Exception as ex:
	print(ex)
