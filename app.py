from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import os
import json
from uuid import uuid4
from termcolor import colored, cprint
from flask_cors import CORS, cross_origin

# Loads environment variables using dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from audio import audio

app = Flask(__name__)
CORS(app)

def default():
    return 'Success!'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.add_url_rule('/', view_func = default, methods = ['GET'])
socketio = SocketIO(app, cors_allowed_origins="*")

''' BEGIN WEBSOCKET CONNECTIONS AND ROUTES ------------------
'''

@socketio.on('connection')
def handle_connect(data):
    cprint(f'Client Connected', "green")
    print(data)
    socketio.emit('success', {})
    return 'Success'

@socketio.on('audioStream')
def handle_audio(data):
    cprint(f'Received Audio!', "green")
    output_text = audio.process_audiofile(data)
    print(output_text)
    cmd = ""

    if "enhance" in output_text or "enhanced" in output_text:
        cmd = "enhance"
    elif "go back" in output_text or "back" in output_text:
        cmd = "back"
    elif "sus" in output_text:
        cmd = "sus"
    elif "zoom" in output_text:
        cmd = "zoom"
    elif "reset" in output_text:
        cmd = "reset"

    if cmd == "": 
        cprint(f"No commands detected")
        return 'Success'

    cprint(f"Emitting `{cmd}` command", "green")
    emit(cmd, broadcast=True)

@socketio.on('imageStream')
def handle_audio2(data):
    cprint(f'Received Image!', "green")
    # output_state, payload = gestures.process(data)
    output_state = ""

    # Whitelisted states: 
    states = [
        "throw", "point", "swipe", "snap", "zoomin"
    ]

    if output_state not in states: return 'Success'
    cprint(f"Emitting `{output_state}` command", "green")
    emit(output_state, broadcast=True)

@socketio.on('disconnection')
def handle_disconnect():
    cprint(f'Client Disconnected', "red")

if __name__ == '__main__':
    print()
    cprint("--------------------------------------", "cyan")
    cprint("------Running websocket app-----------", "cyan")
    cprint("--------------------------------------", "cyan")
    print()

    socketio.run(app,host='0.0.0.0',port=8000)

