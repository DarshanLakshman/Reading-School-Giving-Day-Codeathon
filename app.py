import os
# Disable sound before initializing pygame
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ['XDG_RUNTIME_DIR'] = '/run/user/$(id -u)'

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Importing CORS
import random
import time
from threading import Thread

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)


# Allow CORS for specific frontend domain
CORS(app, origins=["https://reading-school-giving-day-codeathon.onrender.com"], supports_credentials=True)

# Allow CORS for WebSocket connections
socketio = SocketIO(app, cors_allowed_origins=["https://reading-school-giving-day-codeathon.onrender.com"])
# Game Variables
WIDTH, HEIGHT = 800, 600  # Canvas size
FPS = 60  # Frames per second

# Game 1 (Move the Square)
square_pos = [WIDTH // 2, HEIGHT // 2]  # Initial position of the square
square_velocity = [0, 0]  # Initial movement velocity of the square

# Game 2 (Click the Circle)
circle_pos = [random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)]  # Initial random position of the circle
circle_radius = 30  # Radius of the clickable circle

@app.route('/')
def index():
    # This route serves the main HTML page to the user
    return render_template('index.html')  # The HTML page to be served

# WebSocket event for game state updates
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Game 1: Move the Square - Handle Key Events from the client
@socketio.on('move_square')
def move_square(direction):
    global square_pos, square_velocity
    if direction == "left":
        square_velocity = [-5, 0]  # Move left
    elif direction == "right":
        square_velocity = [5, 0]  # Move right
    elif direction == "up":
        square_velocity = [0, -5]  # Move up
    elif direction == "down":
        square_velocity = [0, 5]  # Move down

# Game 2: Click the Circle - Handle Mouse Click Events
@socketio.on('click_circle')
def click_circle(mouse_pos):
    global circle_pos
    circle_x, circle_y = mouse_pos
    # If the user clicks inside the circle, move the circle to a new position
    if (circle_x - circle_pos[0])**2 + (circle_y - circle_pos[1])**2 <= circle_radius**2:
        circle_pos = [random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)]

# Update Game Logic: Move Square and Send Updates to the Client
def update_game_state():
    global square_pos, square_velocity, circle_pos

    # Update square position based on velocity
    square_pos[0] += square_velocity[0]
    square_pos[1] += square_velocity[1]

    # Keep the square within bounds (the canvas dimensions)
    square_pos[0] = max(0, min(square_pos[0], WIDTH - 50))  # Horizontal bounds
    square_pos[1] = max(0, min(square_pos[1], HEIGHT - 50))  # Vertical bounds

    # Emit game state to the client
    socketio.emit('game_state', {
        'square_pos': square_pos,
        'circle_pos': circle_pos
    })

# Main loop that runs the game logic and sends updates every frame
def game_loop():
    while True:
        update_game_state()  # Update game state
        time.sleep(1 / FPS)  # Wait for the next frame (based on FPS)

# Start the game loop in a separate thread
game_thread = Thread(target=game_loop)
game_thread.daemon = True
game_thread.start()

if __name__ == '__main__':
    # Get the port from the environment variable or use 5000 if not set
    port = int(os.environ.get('PORT'))
    
    # Run the app with the correct host and port for Render
    socketio.run(app, host='0.0.0.0', port=port)  # Use '0.0.0.0' for deployment on Render
