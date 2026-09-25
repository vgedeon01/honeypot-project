import sqlite3

DB = "soc.db"


def get_connection():
    return sqlite3.connect(DB)


def get_count(conn, table):
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]


def main():
    conn = get_connection()

    print("=" * 50)
    print("Cowrie SOC Analyzer")
    print("=" * 50)

    print(f"Events:   {get_count(conn, 'events')}")
    print(f"Sessions: {get_count(conn, 'sessions')}")
    print(f"Commands: {get_count(conn, 'commands')}")
    print(f"Alerts:   {get_count(conn, 'alerts')}")
    
    cursor = conn.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN successful_login = 1 THEN 1 ELSE 0 END)
        FROM sessions
    """)

    total_sessions, successful_logins = cursor.fetchone()

    print("\nLogin statistics:")
    print(f"  Successful logins: {successful_logins}")
    print(f"  Failed/no-login sessions: {total_sessions - successful_logins}")
    
    print("\nTop usernames:")
    cursor = conn.execute("""
        SELECT username, COUNT(*)
        FROM sessions
        WHERE username IS NOT NULL
        GROUP BY username
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)

    for username, count in cursor.fetchall():
        print(f"  {username}: {count}")

    print("\nTop passwords:")
    cursor = conn.execute("""
        SELECT password, COUNT(*)
        FROM sessions
        WHERE password IS NOT NULL
        GROUP BY password
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)

    for password, count in cursor.fetchall():
        print(f"  {password}: {count}")

    print("\nAlert severity:")
    cursor = conn.execute("""
        SELECT severity, COUNT(*)
        FROM alerts
        GROUP BY severity
        ORDER BY COUNT(*) DESC
    """)

    for severity, count in cursor.fetchall():
        print(f"  {severity}: {count}")

    print("\nTop alerting IPs:")
    cursor = conn.execute("""
        SELECT src_ip, COUNT(*)
        FROM alerts
        GROUP BY src_ip
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)

    for src_ip, count in cursor.fetchall():
        print(f"  {src_ip}: {count} alerts")

    print("\nCommand categories:")
    cursor = conn.execute("""
        SELECT category, COUNT(*)
        FROM commands
        GROUP BY category
        ORDER BY COUNT(*) DESC
    """)

    for category, count in cursor.fetchall():
        print(f"  {category}: {count}")
        
    print("\nTop commands:")
    cursor = conn.execute("""
        SELECT command, COUNT(*)
        FROM commands
        GROUP BY command
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)

    for command, count in cursor.fetchall():
        print(f"  {command}: {count}")

    print("\nSession duration:")
    cursor = conn.execute("""
        SELECT
            COUNT(duration),
            AVG(duration),
            MIN(duration),
            MAX(duration)
        FROM sessions
        WHERE duration IS NOT NULL
    """)

    count, average, minimum, maximum = cursor.fetchone()

    if count:
        print(f"  Sessions with duration: {count}")
        print(f"  Average: {average:.1f} seconds")
        print(f"  Shortest: {minimum} seconds")
        print(f"  Longest: {maximum} seconds")
    else:
        print("  No completed sessions yet.")
    
    print("\nTop source IPs:")
    cursor = conn.execute("""
        SELECT src_ip, COUNT(*)
        FROM sessions
        GROUP BY src_ip
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)

    for src_ip, count in cursor.fetchall():
        print(f"  {src_ip}: {count} sessions")

    conn.close()


if __name__ == "__main__":
    main()
