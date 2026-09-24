import sqlite3

DB = "soc.db"

def init_db():
	conn = sqlite3.connect(DB)

	conn.execute("""
		CREATE TABLE IF NOT EXISTS events (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			timestamp TEXT,
			event_id TEXT,
			session TEXT,
			protocol TEXT,
			src_ip TEXT,
			src_port INTEGER,
			dst_ip TEXT,
			dst_port INTEGER,
			sensor TEXT,
			uuid TEXT,
			message TEXT
		)
	""")

	conn.execute("""
		CREATE TABLE IF NOT EXISTS alerts (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			timestamp TEXT,
			alert_type TEXT,
			severity TEXT,
			src_ip TEXT,
			session TEXT,
			description TEXT
		)
	""")

	conn.commit()
	conn.close()

if __name__=="__main__":
	init_db()
	print("Database initialized.")
