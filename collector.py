import hashlib
import json
import os
import time

from database import get_connection


COWRIE_LOG = "/home/vboxuser/cowrie/var/log/cowrie/cowrie.json"


def event_fingerprint(event):
    """
    Generate a unique fingerprint for a Cowrie event.

    Cowrie's UUID identifies the event stream/session and is
    therefore not unique enough for individual events.
    """

    raw = "|".join([
        str(event.get("timestamp", "")),
        str(event.get("eventid", "")),
        str(event.get("session", "")),
        str(event.get("message", "")),
    ])

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def event_exists(event):
    """
    Check whether this exact event already exists.

    For now we use the event fingerprint to compare against
    the existing event data.
    """

    fingerprint = event_fingerprint(event)

    conn = get_connection()

    cursor = conn.execute("""
        SELECT 1
        FROM events
        WHERE
            timestamp = ?
            AND event_id = ?
            AND session = ?
            AND message = ?
        LIMIT 1
    """, (
        event.get("timestamp"),
        event.get("eventid"),
        event.get("session"),
        event.get("message")
    ))

    exists = cursor.fetchone() is not None

    conn.close()

    return exists


def insert_event(event):
    """Insert one Cowrie event if it is not already stored."""

    if event_exists(event):
        return False

    conn = get_connection()

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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    return True

def ensure_session(event):
    """Create a session record if it does not already exist."""

    session_id = event.get("session")

    if not session_id:
        return

    conn = get_connection()

    cursor = conn.execute("""
        SELECT 1
        FROM sessions
        WHERE session_id = ?
        LIMIT 1
    """, (session_id,))

    exists = cursor.fetchone() is not None

    if not exists:
        conn.execute("""
            INSERT INTO sessions (
                session_id,
                start_time,
                src_ip,
                protocol
            )
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            event.get("timestamp"),
            event.get("src_ip"),
            event.get("protocol")
        ))

        conn.commit()

        print(
            f"[SESSION] {session_id} | {event.get('src_ip')}",
            flush=True
        )

    conn.close()

def insert_command(event):
    """Insert a Cowrie command into the commands table."""

    if event.get("eventid") != "cowrie.command.input":
        return

    message = event.get("message", "")

    if not message.startswith("CMD:"):
        return

    command = message[4:].strip()

    if not command:
        return

    conn = get_connection()

    conn.execute("""
        INSERT INTO commands (
            session_id,
            timestamp,
            command,
            category
        )
        VALUES (?, ?, ?, ?)
    """, (
        event.get("session"),
        event.get("timestamp"),
        command,
        None
    ))

    conn.commit()
    conn.close()

    print(
        f"[COMMAND] {event.get('session')} | {command}",
        flush=True
    )

def process_line(line):
    """Process one Cowrie JSON event."""

    try:
        event = json.loads(line)

        if not isinstance(event, dict):
            return

        if insert_event(event):
            print(
                f"[+] {event.get('eventid')} "
                f"| {event.get('src_ip')} "
                f"| {event.get('message', '')}",
                flush=True
            )

        ensure_session(event)
        insert_command(event)

    except json.JSONDecodeError:
        print("[!] Invalid JSON line", flush=True)


def process_existing_events(file):
    """Process events already present in the log."""

    for line in file:
        line = line.strip()

        if line:
            process_line(line)


def watch_file(filepath):
    """Continuously monitor the Cowrie log."""

    print(f"[+] Watching: {filepath}", flush=True)

    current_inode = os.stat(filepath).st_ino

    with open(filepath, "r", encoding="utf-8") as file:

        process_existing_events(file)

        print("[+] Collector started", flush=True)
        print("[+] Waiting for new Cowrie events...", flush=True)

        while True:

            line = file.readline()

            if line:
                process_line(line.strip())
                continue

            time.sleep(0.5)

            try:
                new_inode = os.stat(filepath).st_ino

                if new_inode != current_inode:

                    print(
                        "[+] Log file changed - reopening",
                        flush=True
                    )

                    file.close()

                    current_inode = new_inode

                    file = open(
                        filepath,
                        "r",
                        encoding="utf-8"
                    )

            except FileNotFoundError:
                continue


if __name__ == "__main__":

    try:
        watch_file(COWRIE_LOG)

    except KeyboardInterrupt:
        print("\n[+] Collector stopped.")
