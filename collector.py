import json
import sqlite3
import time

LOG_FILE = "/home/vboxuser/cowrie/var/log/cowrie/cowrie.json"
DB_FILE = "soc.db"

def insert_event(event):
	conn = sqlite3.connect(DB_FILE)

	conn.execute("""
		INSERT INTO events (
			timestamp,
			event_id,
			session,
			protocol,
			src_ip,
			src_port,
			dst_ip,
			dst_port,
			sensor,
			uuid,
			message
		)
		VALUES(?,?,?,?,?,?,?,?,?,?,?)
	""", (
		event.get("timestamp"),
		event.get("eventid"),
		event.get("session"),
		event.get("protocol"),
		event.get("src_ip"),
		event.get("src_port"),
		event.get("dst_ip"),
		event.get("dst_port"),
		event.get("sensor"),
		event.get("uuid"),
		event.get("message")
	))

	conn.commit()
	conn.close()

def process_line(line):
	try:
		event =json.loads(line)
		insert_event(event)

		print(
			f"[+] {event.get('timestamp')}"
			f"{event.get('eventid')}"
			f"{event.get('src.ip')}"
		)

	except json.JSONDecodeError:
		print("[!] Invalid JSON line")

def main():
	print("Starting Cowrie collector...")
	print(f"Reading: {LOG_FILE}")

	with open(LOG_FILE, "r")as file:
		file.seek(0,2)

		while True:
			line = file.readline()

			if not line:
				time.sleep(1)
				continue

			process_line(line)

if __name__ == "__main__":
	main()
