# Import the necessary modules
import os

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pymysql
import threading
import time
import json

# Create the Flask app and the SocketIO object
app = Flask(__name__)
socketio = SocketIO(app)

password = os.environ.get('mysqlpassword')

# Connect to the mariadb database using pymysql
conn = pymysql.connect(
    user="u19105_ZN6GaLQ4XR",
    password=password,
    host="45.140.165.82",
    port=3306,
    database="s19105_vvvscoreboard"
)

# Define a global variable to store the scoreboard data
scoreboard = []


# Define a function to refresh the scoreboard data from the database every second
def refresh_scoreboard():
    global scoreboard
    cur = conn.cursor()
    while True:
        # Execute a query to get the scoreboard data from the database
        cur.execute("SELECT * FROM scoreboard ORDER BY score DESC")
        # Fetch the results as a list of tuples
        results = json.dumps(cur.fetchall())
        conn.commit()
        # Check if the scoreboard data has changed
        if results != scoreboard:
            #If any of the players has reached 10 more points, increment "bois":
            # Update the scoreboard data
            scoreboard = results
            # Emit an event to the client with the new scoreboard data
            socketio.emit("scoreboard_update", scoreboard)
        # Sleep for one second
        time.sleep(3)


# Create a thread to run the refresh_scoreboard function
thread = threading.Thread(target=refresh_scoreboard)
# Start the thread
thread.start()


# Define a function to handle the socket.io connection event
@socketio.on("connect")
def handle_connect():
    # Emit the scoreboard data to the client
    emit("scoreboard_update", scoreboard)


# Define a route for the index page
@app.route("/")
def index():
    # Render the index.html template
    return render_template("index.html")


# Run the app
if __name__ == "__main__":
    socketio.run(app)
