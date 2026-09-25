import sqlite3

from flask import Flask, render_template_string

app = Flask(__name__)

DB = "soc.db"


def get_connection():
    return sqlite3.connect(DB)


@app.route("/")
def index():
    conn = get_connection()

    stats = {}

    for table in ["events", "sessions", "commands", "alerts"]:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]

    cursor = conn.execute("""
        SELECT severity, COUNT(*)
        FROM alerts
        GROUP BY severity
        ORDER BY COUNT(*) DESC
    """)
    alert_severity = cursor.fetchall()

    cursor = conn.execute("""
        SELECT category, COUNT(*)
        FROM commands
        GROUP BY category
        ORDER BY COUNT(*) DESC
    """)
    command_categories = cursor.fetchall()

    cursor = conn.execute("""
        SELECT command, COUNT(*)
        FROM commands
        GROUP BY command
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    top_commands = cursor.fetchall()

    cursor = conn.execute("""
        SELECT
            COUNT(duration),
            AVG(duration),
            MIN(duration),
            MAX(duration)
        FROM sessions
        WHERE duration IS NOT NULL
    """)
    duration_count, average_duration, shortest, longest = cursor.fetchone()

    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Bee Nest</title>
    <meta http-equiv="refresh" content="10">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111827;
            color: #f3f4f6;
            margin: 0;
            padding: 30px;
        }

        h1 {
            margin-bottom: 30px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: #1f2937;
            padding: 25px;
            border-radius: 10px;
        }

        .card h2 {
            margin: 0;
            font-size: 32px;
        }

        .card p {
            margin-bottom: 0;
            color: #9ca3af;
        }

        .section {
            background: #1f2937;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #374151;
        }

        th {
            color: #9ca3af;
        }
    </style>
</head>

<body>

<h1>🐝 Cowrie SOC Dashboard</h1>

<div class="stats">

    <div class="card">
        <h2>{{ stats["events"] }}</h2>
        <p>Events</p>
    </div>

    <div class="card">
        <h2>{{ stats["sessions"] }}</h2>
        <p>Sessions</p>
    </div>

    <div class="card">
        <h2>{{ stats["commands"] }}</h2>
        <p>Commands</p>
    </div>

    <div class="card">
        <h2>{{ stats["alerts"] }}</h2>
        <p>Alerts</p>
    </div>

</div>


<div class="section">

    <h2>Alert Severity</h2>

    <table>
        <tr>
            <th>Severity</th>
            <th>Count</th>
        </tr>

        {% for severity, count in alert_severity %}
        <tr>
            <td>{{ severity }}</td>
            <td>{{ count }}</td>
        </tr>
        {% endfor %}

    </table>

</div>


<div class="section">

    <h2>Command Categories</h2>

    <table>
        <tr>
            <th>Category</th>
            <th>Count</th>
        </tr>

        {% for category, count in command_categories %}
        <tr>
            <td>{{ category }}</td>
            <td>{{ count }}</td>
        </tr>
        {% endfor %}

    </table>

</div>


<div class="section">

    <h2>Top Commands</h2>

    <table>
        <tr>
            <th>Command</th>
            <th>Count</th>
        </tr>

        {% for command, count in top_commands %}
        <tr>
            <td>{{ command }}</td>
            <td>{{ count }}</td>
        </tr>
        {% endfor %}

    </table>

</div>


<div class="section">

    <h2>Session Duration</h2>

    {% if duration_count %}

        <p>Sessions with duration: {{ duration_count }}</p>
        <p>Average: {{ "%.1f"|format(average_duration) }} seconds</p>
        <p>Shortest: {{ shortest }} seconds</p>
        <p>Longest: {{ longest }} seconds</p>

    {% else %}

        <p>No completed sessions yet.</p>

    {% endif %}

</div>

</body>
</html>
    """,
    stats=stats,
    alert_severity=alert_severity,
    command_categories=command_categories,
    top_commands=top_commands,
    duration_count=duration_count,
    average_duration=average_duration,
    shortest=shortest,
    longest=longest
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
